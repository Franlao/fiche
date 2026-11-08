"""Rendu HTML d'une fiche : une page autonome, lisible au téléphone, pour juger sur pièces.

C'est le rendu du labo, pas celui de l'application : il montre chaque type de bloc dans une
forme distincte, la page source de chaque bloc, les extraits cités, et en bas les mesures.
Les formules LaTeX sont rendues par MathJax (sortie SVG, sans police à charger).
"""

from __future__ import annotations

from collections.abc import Mapping
from html import escape

from fiche.course import Course, Passage
from fiche.models import (
    BLOCK_LABELS,
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
  --bg: #f6f7f9; --paper: #ffffff; --fg: #1c2330; --muted: #5b6577; --line: #d7dce5;
  --accent: #2f6fb3; --accent-soft: #e6effa; --def: #2f7a4e; --def-soft: #e3f2e8;
  --warn: #b5541c; --warn-soft: #fbe9dc; --display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #141820; --paper: #1d2330; --fg: #e8ecf2; --muted: #a7b0c0; --line: #343c4c;
  --accent: #7fb0e6; --accent-soft: #1f3048; --def: #74c592; --def-soft: #1f3a2a;
  --warn: #eb9a62; --warn-soft: #43291a; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #141820; --paper: #1d2330; --fg: #e8ecf2; --muted: #a7b0c0; --line: #343c4c;
  --accent: #7fb0e6; --accent-soft: #1f3048; --def: #74c592; --def-soft: #1f3a2a;
  --warn: #eb9a62; --warn-soft: #43291a; color-scheme: dark; }
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.5;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 24px 48px; }
main { max-width: 820px; margin: 0 auto; display: grid; gap: 26px; }
h1, h2, h3, h4 { font-family: var(--display); margin: 0; text-wrap: balance; line-height: 1.2; }
h1 { font-size: clamp(26px, 4vw, 36px); }
h2 { font-size: 22px; padding-top: 18px; border-top: 2px solid var(--accent); }
h3 { font-size: 19px; color: var(--accent); }
h4 { font-size: 16.5px; }
p { margin: 0; }
.kicker { font-size: 13px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.lead { color: var(--muted); font-size: 18px; }
.fil { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px; display: grid; gap: 6px; }
.toc { display: grid; gap: 4px; font-size: 15px; }
.toc a { color: var(--accent); text-decoration: none; }
.toc .chap { font-weight: 700; margin-top: 6px; }
section.unit { display: grid; gap: 14px; }
.bloc { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 14px 18px; display: grid; gap: 8px; min-width: 0; }
.bloc .label { font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.bloc.definition { border-left: 4px solid var(--def); }
.bloc.encadre { border: 2px solid var(--accent); background: var(--accent-soft); }
.bloc.piege { border-left: 4px solid var(--warn); }
.bloc.essentiel { background: var(--def-soft); border-color: var(--def); }
.bloc.texte { border: none; background: transparent; padding: 0 2px; }
.nature { font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--accent); font-weight: 700; }
.enonce { font-size: 18px; }
.conds, .vars { font-size: 15px; color: var(--muted); margin: 0; padding-left: 18px; }
.vars { list-style: none; padding: 0; display: grid; gap: 2px; }
.vars b { color: var(--fg); font-weight: 600; }
table { border-collapse: collapse; width: 100%; font-size: 15.5px; }
th, td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; vertical-align: top; }
th { background: var(--accent-soft); font-weight: 700; }
.table-wrap { overflow-x: auto; }
ol.steps { margin: 0; padding-left: 0; list-style: none; counter-reset: s; display: grid; gap: 8px; }
ol.steps li { counter-increment: s; display: grid; grid-template-columns: 30px 1fr; gap: 10px; align-items: start; }
ol.steps li::before { content: counter(s); width: 26px; height: 26px; border-radius: 50%; background: var(--accent); color: var(--paper); font-weight: 700; display: grid; place-items: center; font-size: 14px; }
ol.steps b { display: block; }
ol.timeline { margin: 0; padding-left: 18px; border-left: 2px solid var(--accent); list-style: none; display: grid; gap: 8px; }
ol.timeline li { position: relative; }
ol.timeline li::before { content: ""; position: absolute; left: -24px; top: 8px; width: 10px; height: 10px; border-radius: 50%; background: var(--accent); }
ol.timeline b { color: var(--accent); margin-right: 6px; }
dl.cases { margin: 0; display: grid; gap: 6px; }
dl.cases div { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 10px; }
dl.cases dt { font-weight: 600; } dl.cases dt::before { content: "Si "; color: var(--muted); font-weight: 400; }
dl.cases dd { margin: 0; } dl.cases dd::before { content: "→ "; color: var(--accent); }
ul.points { margin: 0; padding-left: 20px; display: grid; gap: 4px; }
.pieges { display: grid; gap: 8px; }
.pieges div { display: grid; gap: 2px; }
.pieges .err { color: var(--warn); text-decoration: line-through; text-decoration-thickness: 1px; }
details.q { border-top: 1px solid var(--line); padding: 8px 0; }
details.q summary { cursor: pointer; font-weight: 600; }
details.q p { padding-top: 6px; color: var(--muted); }
.src { font-size: 13px; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 12px; align-items: center; }
.src details { display: inline; } .src summary { cursor: pointer; color: var(--accent); display: inline; }
.src blockquote { margin: 8px 0 0; padding: 8px 12px; border-left: 3px solid var(--line); font-size: 14px; white-space: pre-wrap; color: var(--fg); }
.note { font-size: 14px; color: var(--warn); }
.mesures { font-size: 14px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 14px; display: grid; gap: 4px; }
.mesures ul { margin: 0; padding-left: 18px; }
@media (max-width: 480px) { dl.cases div { grid-template-columns: 1fr; } }
"""

MATHJAX = (
    '<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]],'
    'displayMath:[["$$","$$"],["\\\\[","\\\\]"]]},svg:{fontCache:"global"}};</script>'
    '<script async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script>'
)


def e(text: str) -> str:
    # U+FFFD : caractère perdu à la lecture du PDF, gardé visible mais écrit en entité
    return escape(text, quote=True).replace("�", "&#xFFFD;")


def render_html(fiche: Fiche, course: Course | None = None) -> str:
    passages = course.passage_by_id() if course else {}
    out: list[str] = [
        f"<title>{e(fiche.titre)}</title>",
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap">',
        f"<style>{STYLE}</style>",
        MATHJAX,
        "<main>",
        "<header>",
        f'<p class="kicker">Fiche de révision · gabarit {e(fiche.gabarit.nom)}</p>',
        f"<h1>{e(fiche.titre)}</h1>",
        f'<p class="lead">{e(fiche.accroche)}</p>',
        "</header>",
        f'<div class="fil"><p class="kicker">Fil conducteur</p><p>{e(fiche.fil_conducteur)}</p></div>',
        _toc(fiche),
    ]
    for ci, chapter in enumerate(fiche.chapitres, start=1):
        if chapter.titre:
            out.append(f'<h2 id="c{ci}">{e(chapter.titre)}</h2>')
        for si, section in enumerate(chapter.sections, start=1):
            out.append(_section(section, f"s{ci}-{si}", passages))
    out.append(_mesures(fiche))
    out.append("</main>")
    return "\n".join(out)


def _toc(fiche: Fiche) -> str:
    items: list[str] = ['<nav class="toc"><p class="kicker">Parcours</p>']
    for ci, chapter in enumerate(fiche.chapitres, start=1):
        if chapter.titre:
            items.append(f'<a class="chap" href="#c{ci}">{e(chapter.titre)}</a>')
        for si, section in enumerate(chapter.sections, start=1):
            items.append(f'<a href="#s{ci}-{si}">{e(section.titre)}</a>')
    items.append("</nav>")
    return "\n".join(items)


def _section(section: SectionFiche, anchor: str, passages: Mapping[str, Passage]) -> str:
    parts = [f'<section class="unit" id="{anchor}">', f"<h3>{e(section.titre)}</h3>"]
    if section.statut != "ok":
        parts.append(
            f'<p class="note">Section non rédigée ({section.statut}) : {e(section.message)}</p>'
        )
    elif section.message:
        parts.append(f'<p class="note">{e(section.message)}</p>')
    for entry in section.blocs:
        parts.append(_bloc(entry, passages))
    parts.append("</section>")
    return "\n".join(parts)


def _bloc(entry: BlocFiche, passages: Mapping[str, Passage]) -> str:
    bloc = entry.bloc
    label = BLOCK_LABELS[bloc.type]
    body = _body(bloc)
    title = f"<h4>{e(bloc.titre)}</h4>" if bloc.titre and not isinstance(bloc, EncadreBloc) else ""
    label_html = (
        "" if isinstance(bloc, TexteBloc | EncadreBloc) else f'<span class="label">{label}</span>'
    )
    return f'<article class="bloc {bloc.type}">{label_html}{title}{body}{_sources(entry, passages)}</article>'


def _body(bloc: Bloc) -> str:
    if isinstance(bloc, TexteBloc):
        return f"<p>{e(bloc.contenu)}</p>"
    if isinstance(bloc, DefinitionBloc):
        ex = f'<p class="conds">Exemple : {e(bloc.exemple)}</p>' if bloc.exemple else ""
        return f"<p>{e(bloc.definition)}</p>{ex}"
    if isinstance(bloc, EncadreBloc):
        parts = [
            f'<span class="nature">{NATURE_LABELS.get(bloc.nature, bloc.nature)}</span>',
            f"<h4>{e(bloc.titre)}</h4>",
            f'<p class="enonce">{e(bloc.enonce)}</p>',
        ]
        if bloc.conditions:
            parts.append(
                '<ul class="conds">'
                + "".join(f"<li>{e(c)}</li>" for c in bloc.conditions)
                + "</ul>"
            )
        if bloc.variables:
            parts.append(
                '<ul class="vars">'
                + "".join(
                    f"<li><b>{e(v.symbole)}</b> : {e(v.signification)}</li>" for v in bloc.variables
                )
                + "</ul>"
            )
        if bloc.idee:
            parts.append(f'<p class="conds" style="padding:0">{e(bloc.idee)}</p>')
        return "".join(parts)
    if isinstance(bloc, TableauBloc):
        head = "".join(f"<th>{e(c)}</th>" for c in bloc.colonnes)
        rows = "".join(
            "<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>" for row in bloc.lignes
        )
        return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    if isinstance(bloc, EtapesBloc):
        return (
            '<ol class="steps">'
            + "".join(
                f"<li><span><b>{e(s.titre)}</b>{e(s.detail)}</span></li>" for s in bloc.etapes
            )
            + "</ol>"
        )
    if isinstance(bloc, FriseBloc):
        return (
            '<ol class="timeline">'
            + "".join(f"<li><b>{e(ev.repere)}</b>{e(ev.evenement)}</li>" for ev in bloc.evenements)
            + "</ol>"
        )
    if isinstance(bloc, DecisionBloc):
        return (
            f"<p>{e(bloc.situation)}</p>"
            + '<dl class="cases">'
            + "".join(f"<div><dt>{e(c.si)}</dt><dd>{e(c.alors)}</dd></div>" for c in bloc.cas)
            + "</dl>"
        )
    if isinstance(bloc, ExempleBloc):
        steps = "".join(f"<li><span>{e(s)}</span></li>" for s in bloc.resolution)
        return f'<p><b>Énoncé.</b> {e(bloc.enonce)}</p><ol class="steps">{steps}</ol><p><b>À retenir.</b> {e(bloc.resultat)}</p>'
    if isinstance(bloc, PiegeBloc):
        return (
            '<div class="pieges">'
            + "".join(
                f'<div><span class="err">{e(p.erreur)}</span><span>{e(p.correction)}</span></div>'
                for p in bloc.pieges
            )
            + "</div>"
        )
    if isinstance(bloc, EssentielBloc):
        return '<ul class="points">' + "".join(f"<li>{e(p)}</li>" for p in bloc.points) + "</ul>"
    if isinstance(bloc, AutotestBloc):
        return "".join(
            f'<details class="q"><summary>{e(q.question)}</summary><p>{e(q.reponse)}</p></details>'
            for q in bloc.questions
        )
    return ""


def _sources(entry: BlocFiche, passages: Mapping[str, Passage]) -> str:
    pages = ", ".join(str(p) for p in entry.pages)
    where = f"p. {pages}" if pages else "source non située"
    status = {True: " · vérifié", False: " · non soutenu", None: ""}[entry.verifie]
    quotes = ""
    texts = [passages[pid].text for pid in entry.passage_ids if pid in passages]
    if texts:
        quotes = (
            "<details><summary>voir les extraits</summary>"
            + "".join(f"<blockquote>{e(t.strip())}</blockquote>" for t in texts)
            + "</details>"
        )
    return f'<div class="src"><span>{where}{status}</span>{quotes}</div>'


def _mesures(fiche: Fiche) -> str:
    m = fiche.metrics
    u = fiche.usage
    lines = [
        f"Gabarit {e(fiche.gabarit.id)} v{fiche.gabarit.version}"
        + (f", suggéré ({e(fiche.gabarit.raison)})" if fiche.gabarit.suggere else ""),
        f"{m.get('blocs', 0)} blocs dans {m.get('unites', 0)} unités, part structurée {m.get('part_structuree', 0)}, "
        f"{m.get('blocs_rejetes', 0)} blocs retirés par la vérification",
        f"Notions essentielles nommées : {fiche.couverture.couvertes} / {fiche.couverture.essentielles}",
        f"Rédacteur {e(str(m.get('redacteur', '')))} : {u.calls} appels, {u.input_tokens} jetons entrés, "
        f"{u.output_tokens} sortis, {u.cost_usd} $ ; vérificateur : {u.judge_calls} appels, {u.judge_cost_usd} $",
        f"Durée {m.get('duration_s', 0)} s",
    ]
    errors = "".join(f"<li>{e(err)}</li>" for err in fiche.errors)
    missing = ", ".join(fiche.couverture.manquantes)
    return (
        '<footer class="mesures"><p class="kicker">Mesures du labo</p>'
        + "".join(f"<p>{line}</p>" for line in lines)
        + (f"<p>Notions essentielles absentes : {e(missing)}</p>" if missing else "")
        + (f"<ul>{errors}</ul>" if errors else "")
        + "</footer>"
    )
