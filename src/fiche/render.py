"""Rendu HTML d'une fiche : la forme de la fiche telle que les gabarits la conçoivent.

Une fiche se lit comme un document fait par une personne soigneuse, pas comme un empilement de
cartes : titres qui portent l'idée, têtes de paragraphe intégrées au texte (« Théorème. … »),
pages sources dans la marge, un seul encadré pour ce qui se sait par cœur, l'idée fausse barrée
dans les pièges, « À retenir » et « Teste-toi » qui ferment le chapitre. Pas d'étiquette en
capitales au-dessus des titres, pas de barre de couleur sur le côté, pas de symbole à la place
de la mise en forme.

C'est le rendu du labo : l'écran de l'application viendra avec l'identité visuelle de wiliyu.
Les formules LaTeX sont rendues par MathJax (sortie SVG).
"""

from __future__ import annotations

from collections.abc import Mapping
from html import escape

from fiche.course import Course, Passage
from fiche.models import (
    AutotestBloc,
    Bloc,
    BlocFiche,
    DecisionBloc,
    DefinitionBloc,
    EncadreBloc,
    EssentielBloc,
    EtapesBloc,
    ExempleBloc,
    Fiche,
    FriseBloc,
    PiegeBloc,
    SectionFiche,
    TableauBloc,
    TexteBloc,
)

NATURE_LABELS = {
    "theoreme": "Théorème",
    "propriete": "Propriété",
    "formule": "Formule",
    "regle": "Règle",
    "loi": "Loi",
    "principe": "Principe",
}

STYLE = """
:root {
  --ground: #fbfbf9; --ink: #1b1d22; --soft: #5d6370; --rule: #d9dbe0; --rule-strong: #1b1d22;
  --accent: #2346b8; --box: #eef1f9; --alert: #b3401a;
  --head: "Schibsted Grotesk", "Avenir Next", "Segoe UI", sans-serif;
  --text: "Atkinson Hyperlegible Next", "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --ground: #15171b; --ink: #e8e9ec; --soft: #a4a9b5; --rule: #343841; --rule-strong: #e8e9ec;
  --accent: #8fa8ff; --box: #1e2330; --alert: #f08b62; color-scheme: dark; } }
:root[data-theme="dark"] {
  --ground: #15171b; --ink: #e8e9ec; --soft: #a4a9b5; --rule: #343841; --rule-strong: #e8e9ec;
  --accent: #8fa8ff; --box: #1e2330; --alert: #f08b62; color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--ground); color: var(--ink); font-family: var(--text); font-size: 17px; line-height: 1.6;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 40px 64px; }
::selection { background: var(--box); color: var(--ink); }
main { max-width: 860px; margin: 0 auto; display: grid; grid-template-columns: 72px minmax(0, 1fr); column-gap: 28px; }
main > * { grid-column: 2; }
@media (max-width: 640px) { main { grid-template-columns: minmax(0, 1fr); } main > * { grid-column: 1; } }
h1, h2, h3, h4 { font-family: var(--head); margin: 0; line-height: 1.2; text-wrap: balance; }
p { margin: 0; }
a { color: var(--accent); text-underline-offset: 3px; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

.titre { display: grid; gap: 14px; padding-bottom: 28px; border-bottom: 2px solid var(--rule-strong); margin-bottom: 28px; }
.titre h1 { font-size: clamp(30px, 5vw, 44px); font-weight: 800; letter-spacing: -0.02em; }
.titre .accroche { font-size: 20px; line-height: 1.5; max-width: 34em; }
.fil { display: grid; gap: 8px; margin-bottom: 28px; max-width: 38em; }
.fil h2 { font-size: 17px; }
.fil p { color: var(--soft); }
.sommaire { margin: 0 0 40px; padding: 0; list-style: none; display: grid; gap: 2px; font-size: 16px; }
.sommaire li { display: flex; gap: 12px; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--rule); }
.sommaire li.chap { font-family: var(--head); font-weight: 700; border-bottom-color: var(--rule-strong); padding-top: 14px; }
.sommaire a { color: var(--ink); text-decoration: none; }
.sommaire a:hover { color: var(--accent); }
.sommaire span { color: var(--soft); font-variant-numeric: tabular-nums; white-space: nowrap; }

h2.chapitre { font-size: 28px; font-weight: 800; letter-spacing: -0.01em; margin: 48px 0 6px; }
h3.section { font-size: 21px; font-weight: 700; margin: 34px 0 14px; }
.note { color: var(--alert); font-size: 15px; margin-bottom: 12px; }

.bloc { position: relative; margin: 0 0 22px; display: grid; gap: 8px; min-width: 0; }
.page { position: absolute; left: -100px; top: 3px; width: 72px; text-align: right; font-size: 13px; color: var(--soft); font-variant-numeric: tabular-nums; }
@media (max-width: 640px) { .page { position: static; width: auto; text-align: left; order: 9; } }
.runin { font-family: var(--head); font-weight: 700; }
h4 { font-size: 17px; }

.encadre { border: 1.5px solid var(--rule-strong); background: var(--box); border-radius: 4px; padding: 16px 20px; }
.encadre .page { left: -102px; top: 19px; }
.encadre .tete { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; flex-wrap: wrap; }
.encadre .nature { font-size: 14px; letter-spacing: .04em; font-variant: small-caps; color: var(--soft); }
.encadre .enonce { font-size: 18px; }
.encadre ul { margin: 0; padding-left: 20px; }
.encadre .ou, .encadre .idee { font-size: 15.5px; color: var(--soft); }

.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 15.5px; font-variant-numeric: tabular-nums; border-top: 2px solid var(--rule-strong); border-bottom: 2px solid var(--rule-strong); }
th { font-family: var(--head); font-weight: 700; text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--rule-strong); vertical-align: bottom; }
td { padding: 7px 10px; border-bottom: 1px solid var(--rule); vertical-align: top; }
tr:last-child td { border-bottom: 0; }

ol.etapes { margin: 0; padding: 0; list-style: none; counter-reset: e; display: grid; gap: 10px; }
ol.etapes li { counter-increment: e; display: grid; grid-template-columns: 34px minmax(0, 1fr); }
ol.etapes li::before { content: counter(e); font-family: var(--head); font-weight: 800; font-size: 24px; line-height: 1.1; color: var(--accent); font-variant-numeric: tabular-nums; }

dl.frise { margin: 0; display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 6px 18px; }
dl.frise dt { font-family: var(--head); font-weight: 700; font-variant-numeric: tabular-nums; }
dl.frise dd { margin: 0; }

ul.cas { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
ol.resolution { margin: 0; padding-left: 22px; display: grid; gap: 4px; }

.pieges { display: grid; gap: 10px; }
.pieges .attention { color: var(--alert); }
.pieges s { text-decoration-color: var(--alert); text-decoration-thickness: 2px; color: var(--soft); }

.retenir { border-top: 2px solid var(--rule-strong); padding-top: 16px; margin-top: 30px; }
.retenir .page { top: 19px; }
.retenir ul { margin: 0; padding-left: 20px; display: grid; gap: 6px; }

.teste details { border-bottom: 1px solid var(--rule); padding: 9px 0; }
.teste summary { cursor: pointer; }
.teste summary::marker { color: var(--accent); }
.teste details p { padding: 6px 0 2px 18px; color: var(--soft); }

.sources { font-size: 14px; }
.sources summary { cursor: pointer; color: var(--soft); }
.sources blockquote { margin: 8px 0 0; padding: 4px 0 4px 14px; border-left: 1px solid var(--rule); white-space: pre-wrap; color: var(--soft); }

.mesures { margin-top: 56px; padding-top: 14px; border-top: 1px solid var(--rule); font-size: 14px; color: var(--soft); display: grid; gap: 4px; }
.mesures h2 { font-size: 15px; color: var(--ink); }
.mesures ul { margin: 0; padding-left: 18px; }
"""

MATHJAX = (
    '<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]],'
    'displayMath:[["$$","$$"],["\\\\[","\\\\]"]]},svg:{fontCache:"global"}};</script>'
    '<script async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script>'
)

GENERIC_TITLES = {"l'essentiel", "l'essentiel à retenir", "à retenir", "teste-toi", "testez-vous"}


def e(text: str) -> str:
    # U+FFFD : caractère perdu à la lecture du PDF, gardé visible mais écrit en entité
    return escape(text, quote=True).replace("�", "&#xFFFD;")


def _sentence(text: str) -> str:
    """Texte qui se termine par une ponctuation forte, pour les têtes intégrées."""
    text = text.strip()
    return text if text[-1:] in ".?!:" else text + "."


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text[:2] != text[:2].upper() else text


def _pages(entries: list[BlocFiche]) -> str:
    pages = sorted({p for entry in entries for p in entry.pages})
    if not pages:
        return ""
    return f"p. {pages[0]}" if pages[0] == pages[-1] else f"p. {pages[0]} à {pages[-1]}"


def render_html(fiche: Fiche, course: Course | None = None) -> str:
    passages = course.passage_by_id() if course else {}
    out: list[str] = [
        f"<title>{e(fiche.titre)}</title>",
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@600;700;800&family=Atkinson+Hyperlegible+Next:wght@400;700&display=swap">',
        f"<style>{STYLE}</style>",
        MATHJAX,
        '<main lang="fr">',
        '<header class="titre">',
        f"<h1>{e(fiche.titre)}</h1>",
        f'<p class="accroche">{e(fiche.accroche)}</p>',
        "</header>",
        f'<section class="fil"><h2>Le fil du cours</h2><p>{e(fiche.fil_conducteur)}</p></section>',
        _sommaire(fiche),
    ]
    for ci, chapter in enumerate(fiche.chapitres, start=1):
        if chapter.titre:
            out.append(f'<h2 class="chapitre" id="c{ci}">{e(chapter.titre)}</h2>')
        for si, section in enumerate(chapter.sections, start=1):
            out.append(_section(section, f"s{ci}-{si}", passages))
    out.append(_mesures(fiche))
    out.append("</main>")
    return "\n".join(out)


def _sommaire(fiche: Fiche) -> str:
    items: list[str] = ['<ol class="sommaire" aria-label="Sommaire">']
    for ci, chapter in enumerate(fiche.chapitres, start=1):
        if chapter.titre:
            chapter_blocs = [b for s in chapter.sections for b in s.blocs]
            items.append(
                f'<li class="chap"><a href="#c{ci}">{e(chapter.titre)}</a><span>{_pages(chapter_blocs)}</span></li>'
            )
        for si, section in enumerate(chapter.sections, start=1):
            items.append(
                f'<li><a href="#s{ci}-{si}">{e(section.titre)}</a><span>{_pages(section.blocs)}</span></li>'
            )
    items.append("</ol>")
    return "\n".join(items)


def _section(section: SectionFiche, anchor: str, passages: Mapping[str, Passage]) -> str:
    parts = [f'<h3 class="section" id="{anchor}">{e(section.titre)}</h3>']
    if section.statut != "ok":
        parts.append(
            f'<p class="note">Section non rédigée ({section.statut}) : {e(section.message)}</p>'
        )
    elif section.message:
        parts.append(f'<p class="note">{e(section.message)}</p>')
    for entry in section.blocs:
        parts.append(_bloc(entry, passages))
    return "\n".join(parts)


def _bloc(entry: BlocFiche, passages: Mapping[str, Passage]) -> str:
    bloc = entry.bloc
    classes = {"encadre": "bloc encadre", "essentiel": "bloc retenir", "autotest": "bloc teste"}
    css = classes.get(bloc.type, "bloc")
    page = _pages([entry])
    margin = f'<span class="page">{page}</span>' if page else ""
    return f'<div class="{css}">{margin}{_body(bloc)}{_sources(entry, passages)}</div>'


def _variables(bloc: EncadreBloc) -> str:
    parts = [f"{e(v.symbole)} {e(_lower_first(v.signification))}" for v in bloc.variables]
    if not parts:
        return ""
    joined = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " et " + parts[-1]
    return f'<p class="ou">Où {joined}.</p>'


def _body(bloc: Bloc) -> str:
    if isinstance(bloc, TexteBloc):
        head = f"<h4>{e(bloc.titre)}</h4>" if bloc.titre else ""
        return f"{head}<p>{e(bloc.contenu)}</p>"
    if isinstance(bloc, DefinitionBloc):
        ex = f"<p>Par exemple, {e(_lower_first(bloc.exemple))}</p>" if bloc.exemple else ""
        return (
            f'<p><span class="runin">{e(_sentence(bloc.titre))}</span> {e(bloc.definition)}</p>{ex}'
        )
    if isinstance(bloc, EncadreBloc):
        nature = NATURE_LABELS.get(bloc.nature, bloc.nature)
        label = (
            ""
            if bloc.titre.lower().startswith(nature.lower())
            else f'<span class="nature">{nature.lower()}</span>'
        )
        parts = [
            f'<div class="tete"><h4>{e(bloc.titre)}</h4>{label}</div>',
            f'<p class="enonce">{e(bloc.enonce)}</p>',
        ]
        if bloc.conditions:
            word = "Hypothèses" if bloc.nature in ("theoreme", "propriete") else "Conditions"
            items = "".join(f"<li>{e(c)}</li>" for c in bloc.conditions)
            parts.append(f"<p>{word} :</p><ul>{items}</ul>")
        parts.append(_variables(bloc))
        if bloc.idee:
            parts.append(f'<p class="idee">{e(bloc.idee)}</p>')
        return "".join(parts)
    if isinstance(bloc, TableauBloc):
        head = "".join(f'<th scope="col">{e(c)}</th>' for c in bloc.colonnes)
        rows = "".join(
            "<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in bloc.lignes
        )
        return (
            f'<h4>{e(bloc.titre)}</h4><div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>"
        )
    if isinstance(bloc, EtapesBloc):
        steps = "".join(
            f'<li><p><span class="runin">{e(_sentence(s.titre))}</span> {e(s.detail)}</p></li>'
            for s in bloc.etapes
        )
        return f'<h4>{e(bloc.titre)}</h4><ol class="etapes">{steps}</ol>'
    if isinstance(bloc, FriseBloc):
        items = "".join(
            f"<dt>{e(ev.repere)}</dt><dd>{e(ev.evenement)}</dd>" for ev in bloc.evenements
        )
        return f'<h4>{e(bloc.titre)}</h4><dl class="frise">{items}</dl>'
    if isinstance(bloc, DecisionBloc):
        cas = "".join(
            f"<li>Si {e(_lower_first(c.si.rstrip('.')))} : {e(_lower_first(c.alors))}</li>"
            for c in bloc.cas
        )
        return f'<h4>{e(bloc.titre)}</h4><p>{e(bloc.situation)}</p><ul class="cas">{cas}</ul>'
    if isinstance(bloc, ExempleBloc):
        steps = "".join(f"<li>{e(s)}</li>" for s in bloc.resolution)
        return (
            f'<p><span class="runin">Exemple. {e(_sentence(bloc.titre))}</span> {e(bloc.enonce)}</p>'
            f'<ol class="resolution">{steps}</ol>'
            f'<p><span class="runin">Ce qu\'on en retient.</span> {e(bloc.resultat)}</p>'
        )
    if isinstance(bloc, PiegeBloc):
        items = "".join(f"<p><s>{e(p.erreur)}</s> {e(p.correction)}</p>" for p in bloc.pieges)
        return (
            f'<div class="pieges"><h4><span class="attention">Attention.</span> {e(bloc.titre)}</h4>'
            f"{items}</div>"
        )
    if isinstance(bloc, EssentielBloc):
        title = (
            "À retenir du chapitre" if bloc.titre.strip().lower() in GENERIC_TITLES else bloc.titre
        )
        points = "".join(f"<li>{e(p)}</li>" for p in bloc.points)
        return f"<h4>{e(title)}</h4><ul>{points}</ul>"
    if isinstance(bloc, AutotestBloc):
        qs = "".join(
            f"<details><summary>{e(q.question)}</summary><p>{e(q.reponse)}</p></details>"
            for q in bloc.questions
        )
        return f"<h4>Teste-toi</h4>{qs}"
    return ""


def _sources(entry: BlocFiche, passages: Mapping[str, Passage]) -> str:
    texts = [passages[pid].text for pid in entry.passage_ids if pid in passages]
    if not texts:
        return ""
    quotes = "".join(f"<blockquote>{e(t.strip())}</blockquote>" for t in texts)
    return f'<details class="sources"><summary>Voir le passage du cours</summary>{quotes}</details>'


def _mesures(fiche: Fiche) -> str:
    m = fiche.metrics
    u = fiche.usage
    lines = [
        f"Gabarit {e(fiche.gabarit.id)} v{fiche.gabarit.version}"
        + (f", suggéré ({e(fiche.gabarit.raison)})" if fiche.gabarit.suggere else ""),
        f"{m.get('blocs', 0)} blocs dans {m.get('unites', 0)} unités, "
        f"{m.get('blocs_rejetes', 0)} retirés par la vérification",
        f"Notions essentielles nommées : {fiche.couverture.couvertes} sur "
        f"{fiche.couverture.essentielles}",
        f"Écriture : {m.get('tics', 0)} tics pour {m.get('mots', 0)} mots, titres en formule "
        f"{m.get('titres_en_formule', 0)}, monotonie {m.get('monotonie', 0)}",
        f"Rédacteur {e(str(m.get('redacteur', '')))} : {u.calls} appels, {u.cost_usd} $ ; "
        f"vérificateur {u.judge_calls} appels, {u.judge_cost_usd} $",
    ]
    errors = "".join(f"<li>{e(err)}</li>" for err in fiche.errors)
    missing = ", ".join(fiche.couverture.manquantes)
    return (
        '<footer class="mesures"><h2>Mesures du labo</h2>'
        + "".join(f"<p>{line}</p>" for line in lines)
        + (f"<p>Notions essentielles absentes : {e(missing)}</p>" if missing else "")
        + (f"<ul>{errors}</ul>" if errors else "")
        + "</footer>"
    )
