"""La porte d'entrée du module : `run(request) -> Fiche`.

Chaîne : cours (contrat v1) → unités de rédaction → gabarit (donné ou suggéré) → plan de la
fiche (un appel) → blocs par unité (en parallèle) → vérification par un petit modèle →
couverture des notions essentielles → assemblage. Le budget est vérifié avant chaque appel ;
une unité en échec ou hors budget ne bloque pas la fiche.
"""

from __future__ import annotations

import logging
import re
import time
import unicodedata
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from fiche import prompts
from fiche.cache import DiskCache
from fiche.config import Settings, get_settings
from fiche.course import Course, Notion, Passage, Section
from fiche.errors import ProviderError, UnknownGabarit
from fiche.gabarits import Gabarit, load_gabarits
from fiche.llm import LLMProvider, build_judge, build_writer
from fiche.models import (
    BlocFiche,
    ChapitreFiche,
    Couverture,
    Fiche,
    FichePlan,
    GabaritInfo,
    PlanSection,
    SectionBlocs,
    SectionFiche,
    Statut,
    Suggestion,
    Usage,
    Verdicts,
    bloc_as_text,
)
from fiche.request import FicheRequest

log = logging.getLogger(__name__)

MIN_UNIT_CHARS = 1500
"""Des sections consécutives plus courtes sont rédigées ensemble : une section d'une
diapositive ne justifie pas un appel."""
MAX_UNIT_CHARS = 12000
"""Au-delà, les passages d'une section sont répartis en plusieurs unités."""
EventSink = Callable[[str, str], None]
"""`on_event(étape, message)`."""


@dataclass
class Unit:
    """Une unité de rédaction : une ou plusieurs sections consécutives d'un même chapitre."""

    index: int
    title: str
    chapter: Section | None
    sections: list[Section]
    passages: list[Passage]
    notions: list[Notion] = field(default_factory=list)

    @property
    def chars(self) -> int:
        return sum(len(p.text) for p in self.passages)


def writing_units(
    course: Course, min_chars: int = MIN_UNIT_CHARS, max_chars: int = MAX_UNIT_CHARS
) -> list[Unit]:
    units: list[Unit] = []
    for chapter, sections in course.chapters():
        buffer: list[Section] = []
        buffer_passages: list[Passage] = []
        for section in sections:
            passages = course.passages_of(section)
            if len("".join(p.text for p in passages)) > max_chars and not buffer:
                # une section trop longue à elle seule : par tranches de passages
                chunk: list[Passage] = []
                for passage in passages:
                    if chunk and sum(len(p.text) for p in chunk) + len(passage.text) > max_chars:
                        units.append(_unit(len(units) + 1, chapter, [section], chunk, course))
                        chunk = []
                    chunk.append(passage)
                if chunk:
                    units.append(_unit(len(units) + 1, chapter, [section], chunk, course))
                continue
            buffer.append(section)
            buffer_passages.extend(passages)
            if sum(len(p.text) for p in buffer_passages) >= min_chars:
                units.append(_unit(len(units) + 1, chapter, buffer, buffer_passages, course))
                buffer, buffer_passages = [], []
        if buffer:
            last = units[-1] if units and units[-1].chapter is chapter else None
            if last is not None and last.chars < max_chars - min_chars:
                last.sections.extend(buffer)
                last.passages.extend(buffer_passages)
                last.notions = _notions(course, last.sections)
                last.title = _title(chapter, last.sections, len(course.chapters()))
            else:
                units.append(_unit(len(units) + 1, chapter, buffer, buffer_passages, course))
    return units


def _notions(course: Course, sections: list[Section]) -> list[Notion]:
    seen: set[str] = set()
    out: list[Notion] = []
    for section in sections:
        for notion in course.notions_of(section):
            if notion.id not in seen:
                seen.add(notion.id)
                out.append(notion)
    return out


def _title(chapter: Section | None, sections: list[Section], n_chapters: int) -> str:
    titles = [s.title.strip() for s in sections if s.title.strip()]
    if len(titles) == 1:
        return titles[0]
    if chapter is not None and chapter.title.strip() and len(titles) > 2:
        return chapter.title.strip()
    return " · ".join(titles[:3]) if titles else (chapter.title if chapter else "Section")


def _unit(
    index: int,
    chapter: Section | None,
    sections: list[Section],
    passages: list[Passage],
    course: Course,
) -> Unit:
    return Unit(
        index,
        _title(chapter, sections, len(course.chapters())),
        chapter,
        list(sections),
        list(passages),
        _notions(course, sections),
    )


class Budget:
    """Plafond de dépense : la somme des coûts comptés par les fournisseurs (appels abandonnés
    compris), vérifiée avant chaque appel."""

    def __init__(self, max_usd: float, providers: list[LLMProvider]) -> None:
        self.max_usd = max_usd
        self.providers = providers

    @property
    def spent(self) -> float:
        return sum(p.usage.cost_usd for p in self.providers)

    @property
    def exhausted(self) -> bool:
        return self.spent >= self.max_usd


# --- Validateurs métier, renvoyés au modèle -----------------------------------------------------


def check_plan(n_units: int, gabarit: Gabarit) -> Callable[[object], str | None]:
    allowed = set(gabarit.allowed())

    def check(out: object) -> str | None:
        assert isinstance(out, FichePlan)
        numbers = sorted(s.section for s in out.sections)
        if numbers != list(range(1, n_units + 1)):
            return f"Il faut exactement une entrée par section, numérotées de 1 à {n_units}."
        for s in out.sections:
            bad = [b for b in s.blocs if b not in allowed]
            if bad:
                return f"Section {s.section} : blocs non permis par le gabarit : {', '.join(bad)}."
            if not 1 <= len(s.blocs) <= gabarit.max_blocs_par_section:
                return f"Section {s.section} : entre 1 et {gabarit.max_blocs_par_section} blocs."
            if s.blocs.count("texte") > gabarit.max_texte_par_section:
                return f"Section {s.section} : au plus {gabarit.max_texte_par_section} bloc texte."
        return None

    return check


def check_blocs(n_extraits: int, gabarit: Gabarit) -> Callable[[object], str | None]:
    allowed = set(gabarit.allowed())

    def check(out: object) -> str | None:
        assert isinstance(out, SectionBlocs)
        if not out.blocs:
            return "Il faut au moins un bloc : au minimum l'essentiel de la section."
        if len(out.blocs) > gabarit.max_blocs_par_section:
            return f"Au plus {gabarit.max_blocs_par_section} blocs."
        problems: list[str] = []
        for i, b in enumerate(out.blocs, start=1):
            if b.type not in allowed:
                problems.append(f"bloc {i} : type {b.type} non permis")
            if not b.passages:
                problems.append(f"bloc {i} : aucun extrait cité")
            bad = [n for n in b.passages if not 1 <= n <= n_extraits]
            if bad:
                problems.append(f"bloc {i} : extraits inexistants {bad} (de 1 à {n_extraits})")
            if b.type == "tableau":
                if not 2 <= len(b.colonnes) <= 6 or not b.lignes:
                    problems.append(f"bloc {i} : un tableau a 2 à 6 colonnes et au moins une ligne")
                elif any(len(row) != len(b.colonnes) for row in b.lignes):
                    problems.append(
                        f"bloc {i} : chaque ligne doit avoir {len(b.colonnes)} cellules"
                    )
            elif b.type == "etapes" and len(b.etapes) < 2:
                problems.append(f"bloc {i} : au moins deux étapes")
            elif b.type == "frise" and len(b.evenements) < 2:
                problems.append(f"bloc {i} : au moins deux repères")
            elif b.type == "decision" and len(b.cas) < 2:
                problems.append(f"bloc {i} : au moins deux cas")
            elif b.type == "piege" and not b.pieges:
                problems.append(f"bloc {i} : aucun piège")
            elif b.type == "essentiel" and not b.points:
                problems.append(f"bloc {i} : aucun point")
            elif b.type == "autotest" and not 1 <= len(b.questions) <= 5:
                problems.append(f"bloc {i} : 1 à 5 questions")
        if sum(b.type == "texte" for b in out.blocs) > gabarit.max_texte_par_section:
            problems.append(f"au plus {gabarit.max_texte_par_section} bloc texte")
        return "Corrige : " + " ; ".join(problems) + "." if problems else None

    return check


def check_verdicts(n_blocs: int) -> Callable[[object], str | None]:
    def check(out: object) -> str | None:
        assert isinstance(out, Verdicts)
        numbers = sorted(v.bloc for v in out.verdicts)
        if numbers != list(range(1, n_blocs + 1)):
            return f"Il faut un verdict par bloc, numérotés de 1 à {n_blocs}."
        return None

    return check


def check_suggestion(ids: list[str]) -> Callable[[object], str | None]:
    def check(out: object) -> str | None:
        assert isinstance(out, Suggestion)
        if out.gabarit not in ids:
            return f"Le gabarit doit être l'un de : {', '.join(ids)}."
        return None

    return check


# --- Les appels ----------------------------------------------------------------------------------


def _extraits(passages: list[Passage]) -> str:
    return "\n\n".join(f"[{i}] {p.text.strip()}" for i, p in enumerate(passages, start=1))


def _plan_user(course: Course, units: list[Unit]) -> str:
    lines: list[str] = []
    for u in units:
        head = f"[{u.index}] {u.title}"
        if u.chapter is not None and u.chapter.title.strip() and u.chapter.title != u.title:
            head += f" (chapitre : {u.chapter.title.strip()})"
        lines.append(head)
        if u.notions:
            for n in sorted(u.notions, key=lambda n: -n.importance)[:12]:
                definition = " ".join(n.definition.split())[:160]
                lines.append(f"  - {n.name} ({n.type}, importance {n.importance}) : {definition}")
        elif u.passages:
            lines.append("  " + " ".join(u.passages[0].text.split())[:300])
        lines.append(f"  ({len(u.passages)} extraits, {u.chars} caractères)")
    return prompts.PLAN_USER.format(titre=course.document.title, sections="\n".join(lines))


def suggest_gabarit(
    writer: LLMProvider, course: Course, units: list[Unit], gabarits: dict[str, Gabarit]
) -> tuple[Gabarit, str, float]:
    ordered = [gabarits[k] for k in sorted(gabarits)]
    plan = "\n".join(f"- {u.title}" for u in units[:40])
    out, cost = writer.structured(
        prompts.suggest_system(ordered),
        prompts.SUGGEST_USER.format(titre=course.document.title, plan=plan),
        Suggestion,
        check_suggestion([g.id for g in ordered]),
    )
    return gabarits[out.gabarit], out.raison, cost


def make_plan(
    writer: LLMProvider, course: Course, units: list[Unit], gabarit: Gabarit
) -> tuple[FichePlan, float]:
    return writer.structured(
        prompts.plan_system(gabarit),
        _plan_user(course, units),
        FichePlan,
        check_plan(len(units), gabarit),
    )


def write_unit(
    writer: LLMProvider, unit: Unit, plan: FichePlan, planned: PlanSection, gabarit: Gabarit
) -> tuple[SectionBlocs, float]:
    user = prompts.BLOCS_USER.format(
        fiche_titre=plan.titre,
        fil=" ".join(plan.fil_conducteur.split()),
        titre=planned.titre,
        blocs=", ".join(planned.blocs),
        consigne=" ".join(planned.consigne.split()),
        extraits=_extraits(unit.passages),
    )
    return writer.structured(
        prompts.blocs_system(gabarit), user, SectionBlocs, check_blocs(len(unit.passages), gabarit)
    )


def judge_unit(judge: LLMProvider, unit: Unit, blocs: SectionBlocs) -> tuple[Verdicts, float]:
    shown = "\n\n".join(
        f"({i}) {b.type} « {b.titre} » [extraits {', '.join(map(str, b.passages))}]\n{bloc_as_text(b)}"
        for i, b in enumerate(blocs.blocs, start=1)
    )
    user = prompts.JUDGE_USER.format(extraits=_extraits(unit.passages), blocs=shown)
    return judge.structured(prompts.JUDGE_SYSTEM, user, Verdicts, check_verdicts(len(blocs.blocs)))


# --- Couverture ----------------------------------------------------------------------------------


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _mentioned(name: str, haystack: str) -> bool:
    norm = _normalize(name)
    if norm and norm in haystack:
        return True
    words = [w for w in norm.split() if len(w) > 3]
    if not words:
        return False
    hits = sum(w in haystack for w in words)
    return hits / len(words) >= 0.6


def coverage(course: Course, fiche_text: str) -> Couverture:
    """Les notions essentielles (importance 3) que la fiche nomme."""
    haystack = _normalize(fiche_text)
    essential = [n for n in course.notions if n.importance >= 3]
    missing = [n.name for n in essential if not _mentioned(n.name, haystack)]
    return Couverture(
        essentielles=len(essential), couvertes=len(essential) - len(missing), manquantes=missing
    )


# --- Orchestration -------------------------------------------------------------------------------


@dataclass
class _UnitResult:
    unit: Unit
    planned: PlanSection
    statut: Statut = "ok"
    message: str = ""
    blocs: SectionBlocs | None = None
    verdicts: Verdicts | None = None


def run(
    request: FicheRequest,
    settings: Settings | None = None,
    *,
    writer: LLMProvider | None = None,
    judge: LLMProvider | None = None,
    on_event: EventSink | None = None,
) -> Fiche:
    """Produit la fiche d'un cours. Lève InvalidCourse, UnknownGabarit, ou ProviderError quand
    le plan (indispensable) n'a pas pu être obtenu ; les échecs par section sont dans la fiche."""
    started = time.time()
    settings = request.settings(settings or get_settings())
    emit = on_event or (lambda step, msg: None)
    course = Course.load(request.course)
    cache = DiskCache(settings.cache_dir, settings.cache_enabled)
    writer = writer or build_writer(settings, cache)
    if judge is None and settings.verify:
        judge = build_judge(settings, cache)
    gabarits = load_gabarits(settings.gabarits_dir)
    providers = [writer] if judge is None or judge is writer else [writer, judge]
    budget = Budget(settings.max_cost_usd, providers)
    units = writing_units(course)
    emit("unites", f"{len(units)} unités de rédaction pour {len(course.leaf_sections())} sections")

    if request.gabarit is not None:
        if request.gabarit not in gabarits:
            raise UnknownGabarit(request.gabarit, sorted(gabarits))
        gabarit = gabarits[request.gabarit]
        info = GabaritInfo(id=gabarit.id, version=gabarit.version, nom=gabarit.nom)
    else:
        gabarit, raison, _cost = suggest_gabarit(writer, course, units, gabarits)
        info = GabaritInfo(
            id=gabarit.id, version=gabarit.version, nom=gabarit.nom, suggere=True, raison=raison
        )
        emit("gabarit", f"suggéré : {gabarit.nom} ({raison})")

    plan, _cost = make_plan(writer, course, units, gabarit)
    by_number = {s.section: s for s in plan.sections}
    emit("plan", f"{plan.titre} : {sum(len(s.blocs) for s in plan.sections)} blocs prévus")

    def one(unit: Unit) -> _UnitResult:
        result = _UnitResult(unit, by_number[unit.index])
        if budget.exhausted:
            result.statut, result.message = "budget", "plafond de dépense atteint avant l'appel"
            return result
        try:
            assert writer is not None
            result.blocs, _cost = write_unit(writer, unit, plan, result.planned, gabarit)
        except ProviderError as exc:
            result.statut, result.message = "echec", str(exc)
            log.warning("unité %s : %s", unit.index, exc)
            return result
        if judge is not None and result.blocs.blocs:
            if budget.exhausted:
                result.message = "non vérifié : plafond de dépense atteint"
                return result
            try:
                result.verdicts, _cost = judge_unit(judge, unit, result.blocs)
            except ProviderError as exc:
                result.message = f"non vérifié : {exc}"
                log.warning("unité %s, vérification : %s", unit.index, exc)
        emit("section", f"{unit.title} : {len(result.blocs.blocs)} blocs")
        return result

    with ThreadPoolExecutor(max_workers=max(1, settings.llm_concurrency)) as pool:
        results = list(pool.map(one, units))

    fiche = _assemble(course, gabarit, info, plan, results, writer, judge)
    fiche.metrics["duration_s"] = round(time.time() - started, 1)
    fiche.metrics["budget_usd"] = settings.max_cost_usd
    fiche.metrics["spent_usd"] = round(budget.spent, 4)
    fiche.metrics["prompts_version"] = prompts.VERSION
    emit(
        "fiche",
        f"{len(fiche.blocs())} blocs, {fiche.couverture.couvertes}/{fiche.couverture.essentielles} notions essentielles",
    )
    return fiche


def _assemble(
    course: Course,
    gabarit: Gabarit,
    info: GabaritInfo,
    plan: FichePlan,
    results: list[_UnitResult],
    writer: LLMProvider,
    judge: LLMProvider | None,
) -> Fiche:
    chapters: list[ChapitreFiche] = []
    errors: list[str] = []
    texte_blocs = 0
    for r in results:
        verdict_by_number = {v.bloc: v for v in r.verdicts.verdicts} if r.verdicts else {}
        kept: list[BlocFiche] = []
        rejected: list[BlocFiche] = []
        if r.blocs is not None:
            for i, bloc in enumerate(r.blocs.blocs, start=1):
                refs = sorted({n for n in bloc.passages if 1 <= n <= len(r.unit.passages)})
                passages = [r.unit.passages[n - 1] for n in refs]
                pages = sorted({pg for p in passages for pg in range(p.page_start, p.page_end + 1)})
                verdict = verdict_by_number.get(i)
                entry = BlocFiche(
                    bloc=bloc,
                    passage_ids=[p.id for p in passages],
                    pages=pages,
                    verifie=None if verdict is None else verdict.soutenu,
                )
                if verdict is not None and not verdict.soutenu:
                    rejected.append(entry)
                    errors.append(
                        f"{r.unit.title} : bloc {bloc.type} « {bloc.titre} » retiré : {verdict.probleme}"
                    )
                else:
                    kept.append(entry)
                    texte_blocs += bloc.type == "texte"
        if r.statut != "ok":
            errors.append(f"{r.unit.title} : {r.statut} : {r.message}")
        section = SectionFiche(
            section_id=r.unit.sections[0].id,
            titre=r.planned.titre or r.unit.title,
            statut=r.statut,
            message=r.message,
            blocs=kept,
            rejetes=rejected,
        )
        chapter_id = r.unit.chapter.id if r.unit.chapter else None
        if chapters and chapters[-1].section_id == chapter_id:
            chapters[-1].sections.append(section)
        else:
            chapters.append(
                ChapitreFiche(
                    section_id=chapter_id,
                    titre=r.unit.chapter.title if r.unit.chapter else "",
                    sections=[section],
                )
            )

    fiche = Fiche(
        document_id=course.document.id,
        document_title=course.document.title,
        gabarit=info,
        titre=plan.titre,
        accroche=plan.accroche,
        fil_conducteur=plan.fil_conducteur,
        chapitres=chapters,
        errors=errors,
    )
    text = "\n".join(
        [fiche.titre, fiche.accroche, fiche.fil_conducteur]
        + [bloc_as_text(b.bloc) + " " + b.bloc.titre for b in fiche.blocs()]
    )
    fiche.couverture = coverage(course, text)
    w = writer.usage
    fiche.usage = Usage(
        calls=w.calls,
        cached_calls=w.cached_calls,
        failed_calls=w.failed_calls,
        retries=w.retries,
        input_tokens=w.input_tokens,
        output_tokens=w.output_tokens,
        cost_usd=round(w.cost_usd, 4),
        judge_calls=judge.usage.calls if judge else 0,
        judge_input_tokens=judge.usage.input_tokens if judge else 0,
        judge_output_tokens=judge.usage.output_tokens if judge else 0,
        judge_cost_usd=round(judge.usage.cost_usd, 4) if judge else 0.0,
    )
    total = len(fiche.blocs())
    rejected_total = sum(len(s.rejetes) for s in fiche.sections())
    fiche.metrics.update(
        {
            "unites": len(results),
            "blocs": total,
            "blocs_rejetes": rejected_total,
            "blocs_texte": texte_blocs,
            "part_structuree": round(1 - texte_blocs / total, 3) if total else 0.0,
            "taux_rejet": round(rejected_total / (total + rejected_total), 3)
            if total + rejected_total
            else 0.0,
            "couverture": round(fiche.couverture.couvertes / fiche.couverture.essentielles, 3)
            if fiche.couverture.essentielles
            else 1.0,
            "gabarit": f"{gabarit.id} v{gabarit.version}",
            "redacteur": f"{writer.name}:{writer.model}",
            "verificateur": f"{judge.name}:{judge.model}" if judge else "",
        }
    )
    return fiche
