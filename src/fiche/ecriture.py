"""Écriture : les tics d'IA à éviter dans une fiche, leur mesure, et les corrections sûres.

Deux usages. `tics(texte)` repère les tournures qui trahissent un texte généré (tiret cadratin,
« il est important de », « joue un rôle clé », « ex : »…) : la mesure sert au banc, pas à
redemander au modèle, car une reprise coûte et dégrade la réponse (leçon d'ingest).
`nettoyer(texte)` ne corrige que ce qui se corrige sans risque de changer le sens : les tirets
pris pour une ponctuation, les intervalles écrits avec un tiret, les points de suspension.

La charte complète, lisible par un humain, est dans docs/ecriture.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Tournures repérées, avec le nom sous lequel le banc les compte. Insensibles à la casse.
TICS: dict[str, str] = {
    "tiret": r"\s[—–]\s|—",
    "il est important": r"\bil est (?:important|essentiel|crucial|primordial|fondamental) de\b",
    "il convient": r"\bil convient de (?:noter|souligner|rappeler)\b",
    "notons que": r"\b(?:notons|soulignons|rappelons) que\b",
    "en résumé": r"\b(?:en résumé|en somme|en conclusion|pour résumer|en définitive)\b",
    "rôle clé": r"\bjou(?:e|ent) un rôle (?:clé|crucial|essentiel|central|majeur|fondamental|déterminant)\b",
    "clé adjectif": r"\b(?:notions?|concepts?|éléments?|points?|étapes?|acteurs?|facteurs?) clés?\b",
    "crucial": r"\b(?:crucial|cruciale|cruciaux|primordial|primordiale)\b",
    "au cœur": r"\bau cœur (?:de|du|des)\b",
    "véritable": r"\bvéritables?\b",
    "non seulement": r"\bnon seulement\b",
    "permet de": r"\bpermet(?:tent)? (?:de|d')",
    "ex deux-points": r"\bex\.?\s?:",
    "ainsi,": r"(?:^|[.!?]\s)Ainsi,",
    "en d'autres termes": r"\ben d'autres termes\b",
    "points de suspension": r"\.\.\.|…",
    "exclamation": r"!",
    "gras markdown": r"\*\*",
    "des X aux Y": r"\bdes [\w'’ -]{3,40} aux [\w'’ -]{3,40}(?=[.,;])",
    "émoji": "[\U0001f300-\U0001faff☀-➿]",
}
_COMPILED = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in TICS.items()}


@dataclass(frozen=True)
class Mesure:
    mots: int
    tics: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.tics.values())

    @property
    def pour_mille_mots(self) -> float:
        return round(1000 * self.total / self.mots, 1) if self.mots else 0.0


def tics(texte: str) -> dict[str, int]:
    """Nombre d'occurrences de chaque tic présent dans le texte."""
    found = {name: len(rx.findall(texte)) for name, rx in _COMPILED.items()}
    return {name: n for name, n in found.items() if n}


def mesurer(texte: str) -> Mesure:
    return Mesure(mots=len(texte.split()), tics=tics(texte))


_RANGE = re.compile(r"(\d)\s?[–—-]\s?(\d)")
_DASH_PAIR = re.compile(r"\s[—–]\s([^—–]{1,120}?)\s[—–]\s")
_DASH = re.compile(r"\s*[—–]\s*")
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)")


def nettoyer(texte: str) -> str:
    """Corrections sans risque pour le sens.

    - « 5–15 mM » devient « 5 à 15 mM » ;
    - une incise entre deux tirets devient une incise entre virgules ;
    - un tiret seul pris pour une ponctuation devient une virgule ;
    - les points de suspension disparaissent (une liste ouverte se dit « etc. » ou se complète) ;
    - le gras Markdown (« ** ») disparaît : la fiche met en forme par ses blocs, pas par le gras.
    """
    out = _RANGE.sub(r"\1 à \2", texte)
    out = _DASH_PAIR.sub(r", \1, ", out)
    out = _DASH.sub(", ", out)
    out = _ELLIPSIS.sub("", out)
    out = out.replace("**", "")
    out = re.sub(r",\s*([.,;:])", r"\1", out)
    out = re.sub(r"^\s*,\s*", "", out)
    return re.sub(r"[ \t]{2,}", " ", out).strip()
