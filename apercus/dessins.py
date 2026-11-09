"""Répertoire des schémas : vingt-trois formes dessinées par le code à partir d'une description.

Chaque fonction prend ce que le modèle fournirait (étapes, nœuds, valeurs, repères) et renvoie
le contenu d'un SVG de 680 unités de large. C'est le brouillon du moteur de rendu du bloc
`schema` : si une forme est ici, elle est dessinable par le code. Les couleurs sont les
variables communes aux quatre feuilles de style (--accent, --box, --faint, --alert, --soft,
currentColor), donc les mêmes dessins vivent dans toutes les mises en page.

REPERTOIRE décrit chaque forme pour le document docs/schemas/repertoire.md et la galerie
apercus/schemas.html, avec un exemple inventé. Aucun exemple ne vient d'un cours du banc.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from html import escape
from itertools import pairwise

L = 680  # largeur de tous les dessins
TEXTE = 'style="font-family: var(--text)"'


# ----------------------------------------------------------------------------- primitives

def t(x: float, y: float, s: str, size: int = 15, anchor: str = "middle", fill: str = "currentColor",
      weight: str = "") -> str:
    """Texte, avec retours à la ligne sur \\n, centré verticalement sur y."""
    lignes = s.split("\n")
    dy = size * 1.25
    y0 = y - dy * (len(lignes) - 1) / 2
    w = f' font-weight="{weight}"' if weight else ""
    return "".join(
        f'<text x="{x:.0f}" y="{y0 + i * dy:.0f}" font-size="{size}" text-anchor="{anchor}" '
        f'style="fill: {fill}"{w}>{escape(ligne)}</text>'
        for i, ligne in enumerate(lignes)
    )


def boite(x: float, y: float, w: float, h: float, s: str, fill: str = "var(--box)", size: int = 15,
          stroke: str = "none", rx: int = 12) -> str:
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" '
            f'style="fill: {fill}; stroke: {stroke}" stroke-width="2"/>' + t(x + w / 2, y + h / 2, s, size))


def fleche(x1: float, y1: float, x2: float, y2: float, m: str, stroke: str = "var(--accent)",
           dash: str = "") -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke-width="2.5" '
            f'marker-end="url(#{m})" style="stroke: {stroke}"{d}/>')


def chemin(d: str, m: str = "", stroke: str = "var(--accent)", dash: str = "") -> str:
    mk = f' marker-end="url(#{m})"' if m else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke-width="2.5" style="stroke: {stroke}"{mk}{da}/>'


def marqueur(m: str, fill: str = "var(--accent)") -> str:
    return (f'<defs><marker id="{m}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" style="fill: {fill}"/></marker></defs>')


def svg(h: int, corps: str, label: str) -> str:
    return (f'<svg viewBox="0 0 {L} {h}" role="img" aria-label="{escape(label)}">'
            f'<g {TEXTE} style="fill: currentColor">{corps}</g></svg>')


# ----------------------------------------------------------------------------- enchaînements

def chaine(etapes: list[str], liens: list[str] | None = None) -> str:
    n = len(etapes)
    gap, w, h = 28, (L - 20 - 28 * (n - 1)) / n, 60
    y = 40
    s = marqueur("fl-chaine")
    for i, e in enumerate(etapes):
        x = 10 + i * (w + gap)
        s += boite(x, y, w, h, e)
        if i < n - 1:
            s += fleche(x + w + 3, y + h / 2, x + w + gap - 3, y + h / 2, "fl-chaine")
            if liens and liens[i]:
                s += t(x + w + gap / 2, y - 12, liens[i], 13, fill="var(--soft)")
    return svg(120, s, "Chaîne : " + " puis ".join(etapes))


def cycle(etapes: list[str], centre: str = "") -> str:
    w, h = 190, 56
    pos = [(30, 24), (L - 30 - w, 24), (L - 30 - w, 150), (30, 150)]
    s = marqueur("fl-cycle")
    for (x, y), e in zip(pos, etapes, strict=True):
        s += boite(x, y, w, h, e)
    s += fleche(30 + w + 4, 24 + h / 2, L - 30 - w - 4, 24 + h / 2, "fl-cycle")
    s += fleche(L - 30 - w / 2, 24 + h + 4, L - 30 - w / 2, 150 - 4, "fl-cycle")
    s += fleche(L - 30 - w - 4, 150 + h / 2, 30 + w + 4, 150 + h / 2, "fl-cycle")
    s += fleche(30 + w / 2, 150 - 4, 30 + w / 2, 24 + h + 4, "fl-cycle")
    if centre:
        s += t(L / 2, 115, centre, 14, fill="var(--soft)")
    return svg(230, s, "Cycle : " + ", ".join(etapes) + ", et retour au début")


def boucle(etapes: list[str], retour: str, signe: str = "−") -> str:  # noqa: RUF001
    n = len(etapes)
    gap, w, h, y = 40, (L - 40 - 40 * (n - 1)) / n, 60, 30
    s = marqueur("fl-boucle") + marqueur("fl-boucle-r", "var(--alert)")
    for i, e in enumerate(etapes):
        x = 20 + i * (w + gap)
        s += boite(x, y, w, h, e)
        if i < n - 1:
            s += fleche(x + w + 3, y + h / 2, x + w + gap - 3, y + h / 2, "fl-boucle")
    xd, xf = 20 + (n - 1) * (w + gap) + w / 2, 20 + w / 2
    s += chemin(f"M{xd:.0f} {y + h + 4} V{y + h + 44} H{xf:.0f} V{y + h + 6}", "fl-boucle-r", "var(--alert)")
    s += (f'<circle cx="{L / 2:.0f}" cy="{y + h + 44}" r="14" style="fill: var(--alert-soft); stroke: var(--alert)" stroke-width="2"/>'
          + t(L / 2, y + h + 45, signe, 16, fill="var(--alert)", weight="700"))
    s += t(L / 2, y + h + 72, retour, 13, fill="var(--soft)")
    return svg(185, s, "Boucle : " + " puis ".join(etapes) + " ; " + retour)


def escalier(etapes: list[str]) -> str:
    n = len(etapes)
    w, h, marche = (L - 20) / n, 52, 38
    s = ""
    for i, e in enumerate(etapes):
        x = 10 + i * w
        y = 10 + (n - 1 - i) * marche
        s += (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w - 6:.0f}" height="{h + i * marche:.0f}" rx="10" '
              f'style="fill: var(--box)"/>' + t(x + (w - 6) / 2, y + h / 2, e, 14))
        s += t(x + 14, y + h + i * marche - 10, str(i + 1), 14, "start", "var(--accent)", "800")
    return svg(10 + (n - 1) * marche + h + 12, s, "Escalier : " + ", ".join(etapes))


def couloirs(acteurs: list[str], etapes: list[tuple[int, str]]) -> str:
    n, m = len(acteurs), len(etapes)
    hc, x0, y0 = 76, 110, 14
    w, gap = (L - x0 - 20 - 14 * (m - 1)) / m, 14
    s = marqueur("fl-coul")
    for i, a in enumerate(acteurs):
        y = y0 + i * hc
        s += (f'<rect x="{x0}" y="{y}" width="{L - x0 - 10}" height="{hc - 6}" rx="10" style="fill: var(--faint)"/>'
              + t(x0 - 12, y + (hc - 6) / 2, a, 14, "end", weight="700"))
    centres = []
    for j, (ai, e) in enumerate(etapes):
        x, y = x0 + 10 + j * (w + gap), y0 + ai * hc + 10
        s += boite(x, y, w, hc - 26, e, size=13)
        centres.append((x, y, w, hc - 26))
    for (x, y, w_, h_), (x2, y2, _, h2) in pairwise(centres):
        s += fleche(x + w_ + 2, y + h_ / 2, x2 - 2, y2 + h2 / 2, "fl-coul")
    return svg(y0 + n * hc + 4, s, "Couloirs : " + ", ".join(acteurs))


# ----------------------------------------------------------------------------- organisations

def arbre(racine: str, enfants: list[tuple[str, list[str]]]) -> str:
    n = len(enfants)
    w, h = (L - 40 - 20 * (n - 1)) / n, 52
    s = marqueur("fl-arbre")
    s += boite(L / 2 - 110, 10, 220, h, racine, stroke="var(--accent)")
    for i, (e, petits) in enumerate(enfants):
        x = 20 + i * (w + 20)
        s += chemin(f"M{L / 2} {10 + h} V{92} H{x + w / 2:.0f} V{104}", "fl-arbre")
        s += boite(x, 108, w, h, e)
        for k, p in enumerate(petits):
            s += t(x + w / 2, 108 + h + 22 + k * 20, p, 13, fill="var(--soft)")
    maxp = max((len(p) for _, p in enfants), default=0)
    return svg(108 + h + 30 + maxp * 20, s, "Hiérarchie : " + racine)


def venn(a: str, b: str, inter: str, seul_a: str = "", seul_b: str = "") -> str:
    s = ('<circle cx="280" cy="128" r="100" style="fill: var(--box); fill-opacity: .85; stroke: var(--accent)" stroke-width="2"/>'
         '<circle cx="400" cy="128" r="100" style="fill: var(--alert-soft); fill-opacity: .85; stroke: var(--alert)" stroke-width="2"/>')
    s += t(230, 14, a, 15, weight="700", fill="var(--accent)") + t(450, 14, b, 15, weight="700", fill="var(--alert)")
    s += t(340, 128, inter, 14, weight="700")
    if seul_a:
        s += t(232, 128, seul_a, 13, fill="var(--soft)")
    if seul_b:
        s += t(448, 128, seul_b, 13, fill="var(--soft)")
    return svg(240, s, f"Ensembles : {a} et {b}, en commun {inter}")


def carte_mentale(centre: str, branches: list[tuple[str, list[str]]]) -> str:
    cx, cy = L / 2, 120
    s = (f'<ellipse cx="{cx}" cy="{cy}" rx="92" ry="34" style="fill: var(--box); stroke: var(--accent)" stroke-width="2"/>'
         + t(cx, cy, centre, 16, weight="700"))
    pos = [(110, 40, "end"), (570, 40, "start"), (110, 200, "end"), (570, 200, "start")]
    for (x, y, anchor), (b, sous) in zip(pos, branches, strict=False):
        s += chemin(f"M{cx + (-80 if anchor == 'end' else 80)} {cy + (-14 if y < cy else 14)} Q{x + (40 if anchor == 'end' else -40)} {y} {x + (6 if anchor == 'end' else -6)} {y}")
        s += t(x, y, b, 15, anchor, "var(--accent)", "700")
        for k, so in enumerate(sous):
            s += t(x, y + 20 + k * 18, so, 13, anchor, "var(--soft)")
    return svg(260, s, "Carte mentale : " + centre)


def matrice(axe_x: tuple[str, str], axe_y: tuple[str, str], cases: list[str]) -> str:
    x0, y0, w, h = 150, 30, 240, 90
    s = ""
    fills = ["var(--faint)", "var(--box)", "var(--alert-soft)", "var(--faint)"]
    for i, (c, f) in enumerate(zip(cases, fills, strict=True)):
        x, y = x0 + (i % 2) * (w + 8), y0 + (i // 2) * (h + 8)
        s += boite(x, y, w, h, c, f, 14, rx=10)
    s += t(x0 + w / 2, y0 + 2 * h + 30, axe_x[0], 13, fill="var(--soft)")
    s += t(x0 + w + 8 + w / 2, y0 + 2 * h + 30, axe_x[1], 13, fill="var(--soft)")
    s += t(x0 - 14, y0 + h / 2, axe_y[1], 13, "end", "var(--soft)")
    s += t(x0 - 14, y0 + h + 8 + h / 2, axe_y[0], 13, "end", "var(--soft)")
    return svg(y0 + 2 * h + 48, s, "Matrice deux par deux")


def pyramide(niveaux: list[str]) -> str:
    n = len(niveaux)
    h, top = 46, 10
    s = ""
    for i, niv in enumerate(niveaux):
        y = top + i * h
        wt = 80 + i * (520 / n)
        wb = 80 + (i + 1) * (520 / n)
        s += (f'<path d="M{L / 2 - wt / 2:.0f} {y} H{L / 2 + wt / 2:.0f} L{L / 2 + wb / 2:.0f} {y + h - 4} H{L / 2 - wb / 2:.0f} Z" '
              f'style="fill: var(--box); fill-opacity: {1 - i * 0.18:.2f}; stroke: var(--accent)" stroke-width="1.5"/>'
              + t(L / 2, y + h / 2 - 2, niv, 14))
    return svg(top + n * h + 6, s, "Pyramide : " + ", ".join(niveaux))


# ----------------------------------------------------------------------------- choix

def arbre_decision(question: str, branches: list[tuple[str, str]]) -> str:
    n = len(branches)
    w, h = (L - 40 - 20 * (n - 1)) / n, 56
    s = marqueur("fl-dec")
    s += (f'<rect x="{L / 2 - 150}" y="10" width="300" height="54" rx="27" style="fill: var(--box); stroke: var(--accent)" stroke-width="2"/>'
          + t(L / 2, 37, question, 15, weight="700"))
    for i, (cond, res) in enumerate(branches):
        x = 20 + i * (w + 20)
        s += chemin(f"M{L / 2} 64 V88 H{x + w / 2:.0f} V128", "fl-dec")
        s += t(x + w / 2, 108, cond, 13, fill="var(--accent)", weight="700")
        s += boite(x, 132, w, h, res, "var(--faint)", 14)
    return svg(200, s, "Arbre de décision : " + question)


# ----------------------------------------------------------------------------- temps

def frise(reperes: list[tuple[str, str]]) -> str:
    n = len(reperes)
    x0, x1, y = 50, L - 50, 90
    s = f'<line x1="{x0 - 20}" y1="{y}" x2="{x1 + 20}" y2="{y}" stroke-width="3" style="stroke: var(--accent)"/>'
    for i, (date, ev) in enumerate(reperes):
        x = x0 + i * (x1 - x0) / max(n - 1, 1)
        s += f'<circle cx="{x:.0f}" cy="{y}" r="8" style="fill: var(--box); stroke: var(--accent)" stroke-width="3"/>'
        haut = i % 2 == 0
        s += t(x, y - 32 if haut else y + 30, date, 14, fill="var(--accent)", weight="700")
        s += t(x, y - 56 if haut else y + 56, ev, 13, fill="var(--soft)")
    return svg(170, s, "Frise : " + ", ".join(d for d, _ in reperes))


def periodes(bandes: list[tuple[str, float, float]], echelle: tuple[float, float, str]) -> str:
    mn, mx, unite = echelle
    x0, x1, h, y0 = 170, L - 20, 30, 16
    sx = lambda v: x0 + (v - mn) / (mx - mn) * (x1 - x0)  # noqa: E731
    s = ""
    for i, (label, a, b) in enumerate(bandes):
        y = y0 + i * (h + 10)
        s += (f'<rect x="{sx(a):.0f}" y="{y}" width="{sx(b) - sx(a):.0f}" height="{h}" rx="8" '
              f'style="fill: var(--accent); fill-opacity: {0.9 - i * 0.15:.2f}"/>'
              + t(x0 - 12, y + h / 2, label, 13, "end"))
    yb = y0 + len(bandes) * (h + 10) + 6
    s += f'<line x1="{x0}" y1="{yb}" x2="{x1}" y2="{yb}" stroke-width="1.5" style="stroke: var(--soft)"/>'
    pas = (mx - mn) / 4
    for k in range(5):
        v = mn + k * pas
        s += t(sx(v), yb + 18, f"{v:g}", 12, fill="var(--soft)")
    s += t(x1, yb + 36, unite, 12, "end", "var(--soft)")
    return svg(yb + 46, s, "Périodes : " + ", ".join(b[0] for b in bandes))


def avant_apres(avant: tuple[str, list[str]], apres: tuple[str, list[str]]) -> str:
    w, h = 280, 150
    s = marqueur("fl-aa")
    for x, (titre, lignes), f in ((20, avant, "var(--faint)"), (L - 20 - w, apres, "var(--box)")):
        s += f'<rect x="{x}" y="20" width="{w}" height="{h}" rx="14" style="fill: {f}"/>'
        s += t(x + w / 2, 46, titre, 15, weight="700", fill="var(--accent)")
        for k, li in enumerate(lignes):
            s += t(x + w / 2, 80 + k * 24, li, 14)
    s += fleche(20 + w + 12, 20 + h / 2, L - 20 - w - 12, 20 + h / 2, "fl-aa")
    return svg(190, s, f"Avant et après : {avant[0]}, {apres[0]}")


# ----------------------------------------------------------------------------- quantités

def barres(categories: list[str], valeurs: list[float], unite: str = "") -> str:
    n = len(categories)
    x0, y0, y1 = 60, 20, 170
    w = (L - x0 - 30) / n
    vmax = max(valeurs)
    s = f'<line x1="{x0}" y1="{y1}" x2="{L - 20}" y2="{y1}" stroke-width="1.5" style="stroke: var(--soft)"/>'
    for i, (c, v) in enumerate(zip(categories, valeurs, strict=True)):
        hb = (v / vmax) * (y1 - y0 - 20)
        x = x0 + i * w + w * 0.2
        s += f'<rect x="{x:.0f}" y="{y1 - hb:.0f}" width="{w * 0.6:.0f}" height="{hb:.0f}" rx="6" style="fill: var(--accent)"/>'
        s += t(x + w * 0.3, y1 - hb - 12, f"{v:g}{unite}", 13, weight="700")
        s += t(x + w * 0.3, y1 + 18, c, 13, fill="var(--soft)")
    return svg(200, s, "Barres : " + ", ".join(f"{c} {v:g}{unite}" for c, v in zip(categories, valeurs, strict=True)))


def courbe(points: list[tuple[float, float]], phases: list[tuple[float, float, str]],
           axe_x: str, axe_y: str) -> str:
    x0, x1, y0, y1 = 50, L - 20, 20, 170
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    sx = lambda v: x0 + (v - min(xs)) / (max(xs) - min(xs)) * (x1 - x0)  # noqa: E731
    sy = lambda v: y1 - (v - min(ys)) / (max(ys) - min(ys)) * (y1 - y0 - 10)  # noqa: E731
    s = marqueur("fl-axe", "var(--soft)")
    s += f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke-width="1.5" marker-end="url(#fl-axe)" style="stroke: var(--soft)"/>'
    s += f'<line x1="{x0}" y1="{y1}" x2="{x0}" y2="{y0 - 6}" stroke-width="1.5" marker-end="url(#fl-axe)" style="stroke: var(--soft)"/>'
    for a, b, label in phases:
        s += f'<line x1="{sx(b):.0f}" y1="{y0}" x2="{sx(b):.0f}" y2="{y1}" stroke-width="1" stroke-dasharray="4 4" style="stroke: var(--soft)"/>'
        s += t((sx(a) + sx(b)) / 2, y0 + 26, label, 12, fill="var(--soft)")
    d = "M" + " L".join(f"{sx(x):.0f} {sy(y):.0f}" for x, y in points)
    s += chemin(d, stroke="var(--accent)")
    s += t(x1, y1 + 18, axe_x, 13, "end", "var(--soft)") + t(x0 + 10, y0 + 2, axe_y, 13, "start", "var(--soft)")
    return svg(200, s, f"Courbe : {axe_y} selon {axe_x}, phases " + ", ".join(p[2] for p in phases))


def boites(groupes: list[tuple[str, float, float, float, float, float]], axe: str) -> str:
    n = len(groupes)
    x0, y0, y1 = 60, 20, 170
    vmin = min(g[1] for g in groupes)
    vmax = max(g[5] for g in groupes)
    sy = lambda v: y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)  # noqa: E731
    w = (L - x0 - 30) / n
    s = f'<line x1="{x0 - 10}" y1="{y0}" x2="{x0 - 10}" y2="{y1}" stroke-width="1.5" style="stroke: var(--soft)"/>'
    for v in (vmin, (vmin + vmax) / 2, vmax):
        s += t(x0 - 18, sy(v), f"{v:g}", 12, "end", "var(--soft)")
    for i, (label, mn, q1, med, q3, mx) in enumerate(groupes):
        cx = x0 + i * w + w / 2
        bw = min(w * 0.5, 90)
        s += f'<line x1="{cx:.0f}" y1="{sy(mn):.0f}" x2="{cx:.0f}" y2="{sy(mx):.0f}" stroke-width="2" style="stroke: var(--accent)"/>'
        for v in (mn, mx):
            s += f'<line x1="{cx - bw / 4:.0f}" y1="{sy(v):.0f}" x2="{cx + bw / 4:.0f}" y2="{sy(v):.0f}" stroke-width="2" style="stroke: var(--accent)"/>'
        s += f'<rect x="{cx - bw / 2:.0f}" y="{sy(q3):.0f}" width="{bw:.0f}" height="{sy(q1) - sy(q3):.0f}" rx="4" style="fill: var(--box); stroke: var(--accent)" stroke-width="2"/>'
        s += f'<line x1="{cx - bw / 2:.0f}" y1="{sy(med):.0f}" x2="{cx + bw / 2:.0f}" y2="{sy(med):.0f}" stroke-width="3" style="stroke: var(--accent)"/>'
        s += t(cx, y1 + 20, label, 13, fill="var(--soft)")
    s += t(x0 + 4, y0 - 8, axe, 12, "start", "var(--soft)")
    return svg(200, s, "Boîtes à moustaches : " + ", ".join(g[0] for g in groupes))


def nuage(points: list[tuple[float, float]], axe_x: str, axe_y: str, tendance: bool = True) -> str:
    x0, x1, y0, y1 = 60, L - 20, 20, 170
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    sx = lambda v: x0 + (v - min(xs)) / (max(xs) - min(xs)) * (x1 - x0 - 20) + 10  # noqa: E731
    sy = lambda v: y1 - (v - min(ys)) / (max(ys) - min(ys)) * (y1 - y0 - 20) - 10  # noqa: E731
    s = (f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke-width="1.5" style="stroke: var(--soft)"/>'
         f'<line x1="{x0}" y1="{y1}" x2="{x0}" y2="{y0}" stroke-width="1.5" style="stroke: var(--soft)"/>')
    for x, y in points:
        s += f'<circle cx="{sx(x):.0f}" cy="{sy(y):.0f}" r="6" style="fill: var(--accent); fill-opacity: .75"/>'
    if tendance:
        n = len(points)
        mx, my = sum(xs) / n, sum(ys) / n
        pente = sum((x - mx) * (y - my) for x, y in points) / max(sum((x - mx) ** 2 for x in xs), 1e-9)
        f = lambda x: my + pente * (x - mx)  # noqa: E731
        s += chemin(f"M{sx(min(xs)):.0f} {sy(f(min(xs))):.0f} L{sx(max(xs)):.0f} {sy(f(max(xs))):.0f}", stroke="var(--alert)", dash="6 5")
    s += t(x1, y1 + 18, axe_x, 13, "end", "var(--soft)") + t(x0 + 6, y0 - 4, axe_y, 13, "start", "var(--soft)")
    return svg(200, s, f"Nuage de points : {axe_y} selon {axe_x}")


def jauge(mn: float, mx: float, plage: tuple[float, float], unite: str, reperes: list[tuple[float, str]],
          valeur_label: str) -> str:
    x0, x1, y, h = 40, L - 40, 60, 22
    sx = lambda v: x0 + (v - mn) / (mx - mn) * (x1 - x0)  # noqa: E731
    s = f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="11" style="fill: var(--faint)"/>'
    s += f'<rect x="{sx(plage[0]):.0f}" y="{y}" width="{sx(plage[1]) - sx(plage[0]):.0f}" height="{h}" rx="11" style="fill: var(--accent)"/>'
    s += t((sx(plage[0]) + sx(plage[1])) / 2, y - 16, valeur_label, 15, weight="700", fill="var(--accent)")
    for k, (v, label) in enumerate(reperes):
        # Les libellés alternent à gauche et à droite du seuil, car deux seuils sont souvent proches
        gauche = k % 2 == 0
        s += f'<line x1="{sx(v):.0f}" y1="{y - 4}" x2="{sx(v):.0f}" y2="{y + h + 4}" stroke-width="2" style="stroke: var(--soft)"/>'
        s += t(sx(v), y + h + 22, f"{v:g}", 13, weight="700")
        s += t(sx(v) + (-10 if gauche else 10), y + h + 40, label, 12, "end" if gauche else "start", "var(--soft)")
    s += t(x0, y + h + 22, f"{mn:g}", 12, "start", "var(--soft)") + t(x1, y + h + 22, f"{mx:g} {unite}", 12, "end", "var(--soft)")
    return svg(136, s, f"Jauge : {valeur_label} entre {mn:g} et {mx:g} {unite}")


# ----------------------------------------------------------------------------- comparaisons

def face_a_face(gauche: tuple[str, list[str]], droite: tuple[str, list[str]], criteres: list[str]) -> str:
    n = len(criteres)
    y0, pas = 50, 34
    s = t(L / 2 - 190, 22, gauche[0], 15, weight="700", fill="var(--accent)") + t(L / 2 + 190, 22, droite[0], 15, weight="700", fill="var(--alert)")
    for k in range(n):
        y = y0 + k * pas
        f = "var(--faint)" if k % 2 == 0 else "none"
        s += f'<rect x="20" y="{y - 14}" width="{L - 40}" height="{pas - 4}" rx="8" style="fill: {f}"/>'
        s += t(L / 2, y + 3, criteres[k], 12, fill="var(--soft)", weight="700")
        s += t(L / 2 - 100, y + 3, gauche[1][k], 14, "end") + t(L / 2 + 100, y + 3, droite[1][k], 14, "start")
    return svg(y0 + n * pas, s, f"Face à face : {gauche[0]} et {droite[0]}")


def grille_chaleur(lignes: list[str], colonnes: list[str], niveaux: list[list[int]], legende: list[str]) -> str:
    x0, y0, w, h = 150, 30, (L - 150 - 20) / len(colonnes), 46
    s = ""
    for j, c in enumerate(colonnes):
        s += t(x0 + j * w + w / 2, 16, c, 13, fill="var(--soft)", weight="700")
    for i, li in enumerate(lignes):
        y = y0 + i * h
        s += t(x0 - 12, y + h / 2, li, 13, "end", weight="700")
        for j, niv in enumerate(niveaux[i]):
            op = 0.18 + 0.27 * (niv - 1)
            fill = "var(--alert)" if niv >= 3 else "var(--accent)"
            s += f'<rect x="{x0 + j * w + 3:.0f}" y="{y + 3}" width="{w - 6:.0f}" height="{h - 6}" rx="8" style="fill: {fill}; fill-opacity: {op:.2f}"/>'
            s += t(x0 + j * w + w / 2, y + h / 2, legende[niv - 1], 13)
    return svg(y0 + len(lignes) * h + 6, s, "Grille : " + ", ".join(lignes) + " selon " + ", ".join(colonnes))


# ----------------------------------------------------------------------------- fonctionnement

def _picto(genre: str, x: float, y: float) -> str:
    """Un pictogramme de 60 × 60 dont le coin haut gauche est en (x, y)."""
    a = 'style="fill: var(--accent)"'
    b = 'style="fill: var(--box); stroke: var(--accent)" stroke-width="2"'
    if genre == "personne":
        return f'<circle cx="{x + 30}" cy="{y + 16}" r="12" {a}/><path d="M{x + 8} {y + 60} V{y + 44} a22 16 0 0 1 44 0 V{y + 60} Z" {a}/>'
    if genre == "batiment":
        return f'<path d="M{x + 6} {y + 26} L{x + 30} {y + 6} L{x + 54} {y + 26} Z" {a}/><rect x="{x + 12}" y="{y + 26}" width="36" height="34" {b}/><rect x="{x + 25}" y="{y + 42}" width="10" height="18" {a}/>'
    if genre == "document":
        return f'<path d="M{x + 14} {y + 4} H{x + 38} L{x + 48} {y + 14} V{y + 58} H{x + 14} Z" {b}/>' + "".join(f'<rect x="{x + 21}" y="{y + 22 + k * 9}" width="20" height="3" {a}/>' for k in range(4))
    if genre == "ecran":
        return f'<rect x="{x + 4}" y="{y + 8}" width="52" height="36" rx="4" {b}/><rect x="{x + 24}" y="{y + 44}" width="12" height="8" {a}/><rect x="{x + 16}" y="{y + 52}" width="28" height="4" rx="2" {a}/>'
    if genre == "livre":
        return f'<rect x="{x + 10}" y="{y + 6}" width="40" height="50" rx="3" {b}/><rect x="{x + 10}" y="{y + 6}" width="8" height="50" {a}/>'
    if genre == "horloge":
        return f'<circle cx="{x + 30}" cy="{y + 30}" r="24" {b}/><path d="M{x + 30} {y + 14} V{y + 30} H{x + 42}" fill="none" stroke-width="3" style="stroke: var(--accent)"/>'
    if genre == "boite":
        return f'<rect x="{x + 6}" y="{y + 16}" width="48" height="38" rx="4" {b}/><rect x="{x + 6}" y="{y + 16}" width="48" height="10" {a}/>'
    return f'<rect x="{x + 10}" y="{y + 10}" width="40" height="40" rx="8" {b}/>'


def pictogrammes(elements: list[tuple[str, str, float, float]], fleches: list[tuple[int, int, str]],
                 zones: list[tuple[str, float, float, float, float]] | None = None, hauteur: int = 200) -> str:
    s = marqueur("fl-picto")
    for label, x0, x1, y, h in zones or []:
        s += f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}" rx="14" style="fill: var(--faint)"/>' + t((x0 + x1) / 2, y + 16, label, 12, fill="var(--soft)", weight="700")
    centres = []
    for genre, label, x, y in elements:
        s += _picto(genre, x, y) + t(x + 30, y + 78, label, 13)
        centres.append((x + 30, y + 30))
    for i, j, label in fleches:
        (xa, ya), (xb, yb) = centres[i], centres[j]
        dx, dy = xb - xa, yb - ya
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        s += fleche(xa + ux * 42, ya + uy * 42, xb - ux * 42, yb - uy * 42, "fl-picto")
        if label:
            s += t((xa + xb) / 2, (ya + yb) / 2 - 10, label, 12, fill="var(--soft)")
    return svg(hauteur, s, "Illustration : " + ", ".join(e[1] for e in elements))


def coupe(zones: list[tuple[str, int, str]]) -> str:
    x0, w, y = 40, 380, 16
    s = ""
    for i, (label, h, detail) in enumerate(zones):
        op = 0.95 - i * 0.25
        s += f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" style="fill: var(--box); fill-opacity: {op:.2f}; stroke: var(--accent)" stroke-width="1.5"/>'
        s += f'<line x1="{x0 + w}" y1="{y + h / 2:.0f}" x2="{x0 + w + 30}" y2="{y + h / 2:.0f}" stroke-width="1.5" style="stroke: var(--soft)"/>'
        s += t(x0 + w + 38, y + h / 2 - 8, label, 15, "start", weight="700") + t(x0 + w + 38, y + h / 2 + 12, detail, 13, "start", "var(--soft)")
        y += h
    return svg(y + 16, s, "Coupe : " + ", ".join(z[0] for z in zones))


# ----------------------------------------------------------------------------- répertoire

@dataclass
class Forme:
    id: str
    nom: str
    question: str
    montre_bien: str
    eviter: str
    il_faut: str
    champs: str
    legende: str
    dessin: Callable[[], str]
    exemples_possibles: list[str] = field(default_factory=list)


REPERTOIRE: list[Forme] = [
    Forme("chaine", "Chaîne d'étapes", "un enchaînement",
          "une suite ordonnée de 3 à 6 étapes, chacune déclenchant la suivante.",
          "les étapes sont plus de six (faire deux chaînes), ou le cours ne donne pas d'ordre.",
          "l'ordre des étapes et, s'il y en a, ce qui passe de l'une à l'autre.",
          "etapes (3 à 6), liens (facultatif, un par flèche)",
          "De la lumière au sucre : les quatre temps de la photosynthèse tels que le cours les nomme.",
          lambda: chaine(["Lumière captée", "Eau scindée", "Énergie stockée", "Sucre fabriqué"],
                         ["chlorophylle", "oxygène libéré", "ATP"]),
          ["un protocole", "une chaîne de production", "une réaction en étapes"]),
    Forme("cycle", "Cycle", "un enchaînement",
          "quatre étapes dont la dernière relance la première.",
          "la fin ne relance pas le début : c'est une chaîne, pas un cycle.",
          "que le cours dise explicitement que ça recommence.",
          "etapes (4), centre (facultatif)",
          "Le cycle économique : chaque phase prépare la suivante, et la reprise ramène à l'expansion.",
          lambda: cycle(["Expansion", "Surchauffe", "Récession", "Reprise"], "un cycle dure 6 à 10 ans"),
          ["cycle de l'eau", "cycle cellulaire", "cycle de vie d'un produit"]),
    Forme("boucle", "Boucle de rétroaction", "un enchaînement",
          "un effet qui revient sur sa cause pour la freiner (−) ou l'amplifier (+).",  # noqa: RUF001
          "le retour n'est pas dans le cours : ne pas l'inventer pour faire joli.",
          "la cause, l'effet, et le sens du retour.",
          "etapes (2 à 4), retour (ce que fait le retour), signe (+ ou −)",  # noqa: RUF001
          "La glycémie : l'insuline fait baisser le sucre, ce qui freine la sécrétion d'insuline.",
          lambda: boucle(["Glycémie monte", "Pancréas sécrète l'insuline", "Glycémie baisse"],
                         "la baisse freine la sécrétion : rétroaction négative"),
          ["thermostat", "offre et prix", "emballement d'une rumeur"]),
    Forme("escalier", "Escalier", "un enchaînement",
          "des étapes qui s'ajoutent les unes aux autres, chacune supposant la précédente acquise.",
          "les étapes sont indépendantes : une chaîne suffit.",
          "que chaque étape s'appuie sur la précédente.",
          "etapes (3 à 5)",
          "Les recours contre une décision : on ne saute pas une marche.",
          lambda: escalier(["Réclamation", "Médiation", "Tribunal", "Appel"]),
          ["niveaux de preuve", "paliers d'apprentissage", "degrés de juridiction"]),
    Forme("couloirs", "Couloirs", "un enchaînement",
          "qui fait quoi quand plusieurs acteurs se passent le relais.",
          "il n'y a qu'un acteur : une chaîne suffit.",
          "les acteurs et l'étape dont chacun est responsable.",
          "acteurs (2 à 4), etapes (acteur, texte)",
          "Une commande en ligne : trois acteurs, cinq étapes, le relais passe de l'un à l'autre.",
          lambda: couloirs(["Client", "Boutique", "Livreur"],
                           [(0, "Commande"), (1, "Prépare\nle colis"), (2, "Enlève\nle colis"),
                            (2, "Livre"), (0, "Confirme\nla réception")]),
          ["circuit d'une ordonnance", "procédure législative", "traitement d'une demande"]),
    Forme("arbre", "Hiérarchie", "une organisation",
          "ce qui dépend de quoi : un tout et ses parties, un chef et ses services.",
          "les éléments sont au même niveau : un tableau ou une carte mentale.",
          "le lien de dépendance entre les niveaux.",
          "racine, enfants (2 à 4), petits-enfants (facultatif)",
          "Les trois pouvoirs et ce qu'ils font, sous la Constitution.",
          lambda: arbre("Constitution", [("Exécutif", ["Président", "Gouvernement"]),
                                         ("Législatif", ["Assemblée", "Sénat"]),
                                         ("Judiciaire", ["Tribunaux", "Cours"])]),
          ["classification du vivant", "organigramme", "arborescence de fichiers"]),
    Forme("venn", "Ensembles", "une organisation",
          "deux notions qui se recouvrent en partie : ce qui est propre à chacune, ce qui est commun.",
          "les deux notions ne se recouvrent pas : un face-à-face.",
          "les trois zones : A seul, B seul, commun.",
          "a, b, inter, seul_a, seul_b",
          "Carré, rectangle, losange : le carré est à l'intersection.",
          lambda: venn("Rectangles", "Losanges", "Carrés", "4 angles droits", "4 côtés égaux"),
          ["sciences et techniques", "droit public et privé", "deux maladies aux symptômes communs"]),
    Forme("carte_mentale", "Carte mentale", "une organisation",
          "un sujet central et ses quatre facettes, chacune avec deux ou trois mots.",
          "il y a un ordre entre les branches : une chaîne ou un arbre.",
          "que les branches soient bien des facettes du même sujet, pas des étapes.",
          "centre, branches (4, chacune avec 2 à 3 sous-points)",
          "La cellule vue sous quatre angles, pour réviser d'un coup d'œil.",
          lambda: carte_mentale("La cellule", [("Enveloppe", ["membrane", "paroi (végétaux)"]),
                                              ("Noyau", ["ADN", "nucléole"]),
                                              ("Énergie", ["mitochondries", "chloroplastes"]),
                                              ("Fabrication", ["ribosomes", "réticulum"])]),
          ["un auteur et ses thèmes", "une période et ses aspects", "un concept et ses usages"]),
    Forme("matrice", "Matrice deux par deux", "une organisation",
          "quatre situations définies par deux critères qui ont chacun deux valeurs.",
          "les critères ont plus de deux valeurs : une grille.",
          "les deux critères et ce que le cours met dans chaque case.",
          "axe_x (deux valeurs), axe_y (deux valeurs), cases (4)",
          "Classer les tâches par urgence et importance : la matrice du cours de gestion.",
          lambda: matrice(("pas urgent", "urgent"), ("pas important", "important"),
                          ["Planifier", "Faire maintenant", "Abandonner", "Déléguer"]),
          ["BCG", "risque et rendement", "public et privé croisé avec national et local"]),
    Forme("pyramide", "Pyramide", "une organisation",
          "des niveaux ordonnés du plus fondamental (en bas) au plus élevé, ou du plus nombreux au plus rare.",
          "il n'y a pas d'ordre entre les niveaux.",
          "l'ordre des niveaux et ce qui le fonde.",
          "niveaux (3 à 6, du sommet à la base)",
          "La hiérarchie des normes : chaque étage doit respecter celui du dessus.",
          lambda: pyramide(["Constitution", "Traités", "Lois", "Règlements", "Actes individuels"]),
          ["pyramide des âges", "chaîne alimentaire", "besoins"]),
    Forme("arbre_decision", "Arbre de décision", "un choix",
          "une question et la réponse selon le cas.",
          "il y a plus de trois cas ou des cas emboîtés : le bloc decision en liste.",
          "tous les cas que le cours distingue, aucun ajouté.",
          "question, branches (condition, résultat) × 2 ou 3",
          "Quel temps en anglais ? La question que pose le cours, et ses trois réponses.",
          lambda: arbre_decision("L'action est-elle reliée au présent ?",
                                 [("non, datée et finie", "Prétérit"),
                                  ("oui, par sa durée", "Present perfect"),
                                  ("oui, et elle continue", "Present perfect continuous")]),
          ["quel régime juridique", "quelle conduite devant un symptôme", "quel algorithme"]),
    Forme("frise", "Frise", "le temps",
          "des événements datés, dans l'ordre, sur une ligne.",
          "les événements durent : des périodes.",
          "les dates exactes du cours.",
          "reperes (date, événement) × 3 à 8",
          "Un siècle de régimes politiques en cinq dates.",
          lambda: frise([("1792", "Ire République"), ("1804", "Empire"), ("1814", "Restauration"),
                         ("1830", "Monarchie de Juillet"), ("1848", "IIe République")]),
          ["étapes d'une découverte", "vie d'un auteur", "chronologie d'une réforme"]),
    Forme("periodes", "Périodes", "le temps",
          "des phases qui durent, avec leur début et leur fin, parfois qui se chevauchent.",
          "ce sont des instants : une frise.",
          "les bornes de chaque période.",
          "bandes (nom, début, fin), échelle (min, max, unité)",
          "Les stades du développement selon le cours de psychologie, en années.",
          lambda: periodes([("Sensorimoteur", 0, 2), ("Préopératoire", 2, 7),
                            ("Opérations concrètes", 7, 11), ("Opérations formelles", 11, 16)], (0, 16, "âge en années")),
          ["ères géologiques", "phases d'un projet", "règnes"]),
    Forme("avant_apres", "Avant et après", "le temps",
          "ce qui change entre deux états, point par point.",
          "il y a plus de deux états : une chaîne.",
          "les deux états décrits par le cours, sur les mêmes points.",
          "avant (titre, lignes), apres (titre, lignes)",
          "La mitose : une cellule avant, deux cellules identiques après.",
          lambda: avant_apres(("Avant la mitose", ["1 cellule", "46 chromosomes", "ADN dupliqué"]),
                              ("Après la mitose", ["2 cellules", "46 chromosomes chacune", "génétiquement identiques"])),
          ["une réforme", "une réaction chimique", "une transformation économique"]),
    Forme("barres", "Barres", "des quantités",
          "comparer quelques valeurs entre catégories.",
          "il y a plus de huit catégories, ou les valeurs ne sont pas dans le cours.",
          "les valeurs exactes et leur unité.",
          "categories, valeurs, unite",
          "La composition de l'air : trois chiffres que le cours donne.",
          lambda: barres(["Diazote", "Dioxygène", "Argon", "CO₂ et autres"], [78, 21, 0.9, 0.1], " %"),
          ["répartition d'un budget", "effectifs", "résultats d'une expérience"]),
    Forme("courbe", "Courbe", "des quantités",
          "une évolution continue, avec ses phases ; la forme compte plus que les valeurs.",
          "le cours ne décrit ni valeurs ni allure.",
          "soit des points, soit l'allure (croît, plafonne, décroît) et le nom des phases.",
          "points ou allure, phases (début, fin, nom), axe_x, axe_y",
          "Une population de bactéries : les quatre phases que le cours nomme, sans chiffres.",
          lambda: courbe([(0, 1), (2, 1.2), (4, 3), (6, 8), (8, 9.5), (10, 9.6), (12, 9.4), (14, 6), (16, 3)],
                         [(0, 2.5, "latence"), (2.5, 8.5, "croissance"), (8.5, 12.5, "plateau"), (12.5, 16, "déclin")],
                         "temps", "nombre de bactéries"),
          ["offre et demande", "courbe de Phillips", "cinétique d'une réaction"]),
    Forme("boites", "Boîtes à moustaches", "des quantités",
          "la dispersion de plusieurs groupes : médiane, quartiles, extrêmes.",
          "le cours ne donne que des moyennes : des barres.",
          "les cinq valeurs par groupe, ou les données brutes.",
          "groupes (nom, min, Q1, médiane, Q3, max), axe",
          "Les notes de deux groupes : même médiane, dispersion différente.",
          lambda: boites([("Groupe A", 6, 9, 12, 14, 18), ("Groupe B", 2, 8, 12, 16, 20)], "note sur 20"),
          ["mesures répétées", "salaires par secteur", "tailles par espèce"]),
    Forme("nuage", "Nuage de points", "des quantités",
          "le lien entre deux grandeurs mesurées sur les mêmes individus.",
          "il y a moins de six points, ou pas de lien à montrer.",
          "les couples de valeurs du cours.",
          "points (x, y), axe_x, axe_y, tendance",
          "Taille et masse : les points montent ensemble, la droite résume la tendance.",
          lambda: nuage([(150, 48), (155, 52), (160, 58), (162, 55), (168, 64), (170, 70), (175, 72), (178, 80), (182, 78), (185, 86)],
                        "taille (cm)", "masse (kg)"),
          ["revenu et consommation", "dose et effet", "heures de révision et note"]),
    Forme("jauge", "Jauge", "des quantités",
          "une valeur ou une plage normale sur son échelle, avec des seuils.",
          "il y a plusieurs valeurs à comparer : des barres.",
          "la plage, l'échelle et les seuils donnés par le cours.",
          "min, max, plage, unite, reperes (valeur, nom), valeur_label",
          "Le pH du sang : une plage étroite, deux seuils de danger.",
          lambda: jauge(6.8, 7.8, (7.35, 7.45), "pH", [(7.35, "acidose en dessous"), (7.45, "alcalose au-dessus")], "normal : 7,35 à 7,45"),
          ["température corporelle", "taux légal", "seuil de pauvreté"]),
    Forme("face_a_face", "Face à face", "une comparaison",
          "deux notions comparées critère par critère.",
          "il y a plus de deux notions : un tableau.",
          "les critères et les deux valeurs pour chacun.",
          "gauche (titre, valeurs), droite (titre, valeurs), criteres",
          "Mitose et méiose, sur quatre critères du cours.",
          lambda: face_a_face(("Mitose", ["2", "identiques", "46", "croissance"]),
                              ("Méiose", ["4", "différentes", "23", "reproduction"]),
                              ["cellules produites", "cellules filles", "chromosomes", "rôle"]),
          ["deux auteurs", "deux régimes", "deux algorithmes"]),
    Forme("grille", "Grille de chaleur", "une comparaison",
          "un niveau (faible, moyen, fort) au croisement de deux critères.",
          "les cases contiennent du texte long : un tableau.",
          "le niveau de chaque case, tel que le cours le qualifie.",
          "lignes, colonnes, niveaux (1 à 3), legende",
          "Le risque selon la probabilité et la gravité : la grille du cours de gestion.",
          lambda: grille_chaleur(["Gravité forte", "Gravité moyenne", "Gravité faible"],
                                 ["Rare", "Possible", "Fréquent"],
                                 [[2, 3, 3], [1, 2, 3], [1, 1, 2]], ["faible", "moyen", "fort"]),
          ["compatibilités", "fréquence de symptômes", "matrice de confusion"]),
    Forme("pictogrammes", "Illustration à pictogrammes", "un fonctionnement",
          "qui échange quoi avec qui : des acteurs, des objets, des flux.",
          "il n'y a pas d'acteurs distincts : un diagramme suffit.",
          "les acteurs, les objets et le sens des échanges ; les pictogrammes viennent de la bibliothèque, jamais inventés.",
          "elements (pictogramme, étiquette, position), fleches (de, vers, étiquette), zones",
          "Le circuit d'une ordonnance : le médecin, le patient, la pharmacie, l'assurance.",
          lambda: pictogrammes([("personne", "Médecin", 60, 44), ("document", "Ordonnance", 230, 44),
                                ("personne", "Patient", 400, 44), ("batiment", "Pharmacie", 570, 44),
                                ("boite", "Assurance", 400, 164)],
                               [(0, 1, "rédige"), (1, 2, "remise au"), (2, 3, "présente"),
                                (3, 4, "demande le\nremboursement")],
                               [("Soin", 30, 500, 24, 116)], 260),
          ["un marché", "une procédure", "une chaîne logistique"]),
    Forme("coupe", "Coupe à zones", "un fonctionnement",
          "des couches superposées, chacune avec son nom et son rôle.",
          "la structure n'est pas en couches : c'est une image du cours.",
          "l'ordre des couches et ce que le cours dit de chacune.",
          "zones (nom, épaisseur relative, détail)",
          "Les trois couches de la peau, de la surface à la profondeur.",
          lambda: coupe([("Épiderme", 46, "barrière, se renouvelle"), ("Derme", 80, "vaisseaux, nerfs, collagène"),
                         ("Hypoderme", 64, "graisse, isolation")]),
          ["couches de l'atmosphère", "strates géologiques", "couches réseau"]),
]


def galerie() -> str:
    """Le contenu de pages/schemas.html : une entrée par forme, groupées par question."""
    parts = []
    for i, f in enumerate(REPERTOIRE, 1):
        parts.append(
            f'  <section class="entree">\n  <header>\n'
            f'  <h2 class="partie"><span class="n">{i}</span>{escape(f.nom)} <small>{escape(f.question)}</small></h2>\n'
            f'  <p class="doux cat"><b>Montre bien :</b> {escape(f.montre_bien)} '
            f'<b>À éviter quand :</b> {escape(f.eviter)} '
            f'<b>Il faut que le cours dise :</b> {escape(f.il_faut)}</p>\n'
            f'  </header>\n  <figure class="schema">\n    {f.dessin()}\n'
            f'    <figcaption>{escape(f.legende)}</figcaption>\n  </figure>\n  </section>\n'
        )
    return "\n".join(parts)


def repertoire_markdown() -> str:
    """Le document docs/schemas/repertoire.md, engendré depuis la même liste que la galerie."""
    lignes = [
        "# Répertoire des schémas",
        "",
        "Engendré par `apercus/build.py` depuis `apercus/dessins.py` : ne pas modifier à la main.",
        "La galerie dessinée est `apercus/schemas.html`, et dans chaque mise en page `apercus/mep/schemas-*.html`.",
        "",
        "Le bloc `schema` (décision 2) choisit une forme d'après **ce qu'il y a à montrer**, pas par",
        "habitude. Pour chaque forme : ce qu'elle montre bien, quand ne pas l'utiliser, ce que le cours",
        "doit dire pour qu'on ait le droit de s'en servir, et les champs que le modèle remplit. Le code",
        "dessine ; le modèle décrit. Chaque forme de ce répertoire est dessinée par `dessins.py`, donc",
        "dessinable.",
        "",
        "Trois garde-fous contre la répétition : le plan justifie son choix (`pourquoi_cette_forme`),",
        "le gabarit interdit de reprendre une forme dans le même chapitre si une autre convient, et le",
        "banc mesure la diversité des formes par fiche.",
        "",
        "| # | Forme | Pour montrer | Champs |",
        "|---|---|---|---|",
    ]
    for i, f in enumerate(REPERTOIRE, 1):
        lignes.append(f"| {i} | {f.nom} | {f.question} | `{f.champs}` |")
    question = None
    for i, f in enumerate(REPERTOIRE, 1):
        if f.question != question:
            question = f.question
            lignes += ["", f"## Pour montrer {question}"]
        lignes += [
            "",
            f"### {i}. {f.nom}",
            "",
            f"- **Montre bien** : {f.montre_bien}",
            f"- **À éviter quand** : {f.eviter}",
            f"- **Il faut que le cours dise** : {f.il_faut}",
            f"- **Champs** : `{f.champs}`",
            f"- **Exemple de la galerie** : {f.legende}",
            f"- **Autres cas** : {', '.join(f.exemples_possibles)}.",
        ]
    lignes += [
        "",
        "## Formes à l'étude",
        "",
        "- **Balance** (peser deux séries d'arguments) : proche du face-à-face, à ajouter si un cours",
        "  en a besoin.",
        "- **Carte à zones** (un lieu) : le dessin de contours fidèles n'est pas à la portée du code ;",
        "  c'est la forme `image` du bloc.",
        "- **Image du cours** : la seule forme qui n'est pas dessinée ; elle dépend d'ingest.",
        "",
    ]
    return "\n".join(lignes)
