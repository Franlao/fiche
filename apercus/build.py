"""Construit les aperçus des gabarits : une page par famille, avec une en-tête et un pied
communs (dosage du gabarit). Le contenu de chaque fiche est écrit à la main dans pages/.

Lancer : python build.py (depuis ce dossier).
"""

from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).parent
FONTS = (
    "https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@600;700;800"
    "&family=Atkinson+Hyperlegible+Next:wght@400;700&family=JetBrains+Mono:wght@500&display=swap"
)
MATHJAX = (
    '<script>window.MathJax={tex:{inlineMath:[["$","$"]],displayMath:[["$$","$$"]]},'
    'svg:{fontCache:"global"}};</script>\n'
    '<script async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-svg.js"></script>'
)
AXES = ["Illustrations", "Tableaux", "Texte rédigé", "Formules ou code", "Citations et sources"]

# fichier, classe, nom, matière, titre, accroche, dosage (0 à 5 par axe), formules, ce qu'il met en avant
FAMILLES = [
    ("sciences-formelles", "sf", "Sciences formelles", "Analyse · L1", "Suites numériques",
     "Que deviennent les termes d'une suite quand on avance très loin dans la liste ? Tout le chapitre répond à cette question.",
     [2, 2, 2, 5, 0], True,
     ["Les théorèmes et les formules sur des cartes à part, avec leurs hypothèses.",
      "Une phrase « en mots » après chaque définition formelle.",
      "Un exemple au calcul posé."]),
    ("vivant-sante", "vs", "Santé et vivant", "Physiologie · L2", "La contraction du muscle squelettique",
     "Un geste commence par un signal nerveux et finit par des filaments qui glissent. Entre les deux, une chaîne qu'on peut suivre pas à pas.",
     [5, 4, 2, 1, 0], False,
     ["Les schémas d'abord, dont un à légender qu'on peut masquer.",
      "Les classifications en tableaux, les chiffres clés sur une carte.",
      "Peu de texte : des étapes courtes, un acteur et un verbe par étape."]),
    ("economie-gestion", "eg", "Économie et gestion", "Microéconomie · L1", "Offre, demande et prix d'équilibre",
     "Pourquoi les fraises coûtent moins cher en juin qu'en janvier ? Ce chapitre donne l'outil pour le montrer sur un graphique.",
     [4, 3, 3, 3, 1], True,
     ["Chaque modèle en quatre cases : hypothèses, mécanisme, résultat, limites.",
      "Le graphique à savoir refaire, la formule sur une carte, un exemple chiffré."]),
    ("informatique-technique", "it", "Informatique et technique", "Algorithmique · L1", "La recherche dichotomique",
     "Pour trouver un mot dans un dictionnaire, on l'ouvre au milieu et on élimine une moitié. C'est exactement l'algorithme de ce chapitre.",
     [3, 3, 2, 5, 0], True,
     ["L'algorithme dessiné sur un exemple, puis le pseudo-code numéroté.",
      "La trace d'exécution en tableau, la complexité sur une carte."]),
    ("psychologie", "ps", "Psychologie", "Psychologie de l'apprentissage · L1", "Le conditionnement",
     "Pourquoi un chien salive-t-il en entendant une cloche ? Deux théories expliquent comment un comportement s'apprend : par association, et par ses conséquences.",
     [3, 4, 3, 0, 2], False,
     ["Les courants comparés en tableaux, avec leurs auteurs.",
      "L'expérience phare sur une carte, le principe en schéma."]),
    ("droit", "dr", "Droit", "Droit des obligations · L2", "La formation du contrat",
     "Un contrat naît de la rencontre de deux volontés. Encore faut-il qu'elles soient libres et éclairées : tout le chapitre tourne autour du consentement.",
     [2, 3, 4, 0, 5], False,
     ["Les articles à citer mot pour mot, sur des cartes.",
      "Un tableau pour comparer les régimes, un cas pratique résolu en trois temps."]),
    ("histoire", "hi", "Histoire et sciences sociales", "Histoire moderne · L1", "1789, l'Ancien Régime s'effondre",
     "En quatre mois, la France passe d'une monarchie absolue à une assemblée qui proclame les droits de l'homme. Comment, et pourquoi si vite ?",
     [3, 2, 4, 0, 3], False,
     ["Une frise des repères, les dates clés sur des cartes.",
      "Le document à connaître avec sa grille de lecture, les acteurs en tableau.",
      "Du texte pour expliquer les causes et les enchaînements."]),
    ("lettres-philosophie", "le", "Lettres et philosophie", "Philosophie · L1", "La conscience",
     "Je sais que je pense : est-ce pour autant que je sais tout de moi ? Trois auteurs, trois réponses à cette question.",
     [1, 2, 5, 0, 5], False,
     ["Surtout du texte : la problématique et les thèses, rédigées.",
      "Les citations à retenir sur des cartes, avec leur œuvre.",
      "Un tableau court des auteurs et de leurs thèses."]),
    ("langues", "la", "Langues", "Anglais · L1", "Present perfect ou prétérit ?",
     "« I lived » ou « I have lived » ? Le français ne fait pas la différence, l'anglais si. Une seule question décide : l'action est-elle reliée au présent ?",
     [2, 4, 3, 0, 2], False,
     ["Les formes et les marqueurs en tableaux, la règle sur une carte.",
      "Des phrases d'exemple, et la frise du temps pour voir la différence."]),
]


def page(fichier: str, classe: str, nom: str, matiere: str, titre: str, accroche: str,
         dosage: list[int], maths: bool, points: list[str]) -> str:
    corps = (HERE / "pages" / f"{fichier}.html").read_text(encoding="utf-8")
    jauges = "".join(
        f'<dt>{axe}</dt><dd aria-label="{n} sur 5"><i style="width:{n * 20}%"></i></dd>'
        for axe, n in zip(AXES, dosage, strict=True)
    )
    puces = "".join(f"<li>{p}</li>" for p in points)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titre}, gabarit {nom}</title>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="fiche.css">
{MATHJAX if maths else ""}
</head>
<body class="{classe}">
<main>
  <nav class="haut"><a href="index.html">Tous les gabarits</a><span>Aperçu, contenu inventé</span></nav>
  <header class="titre">
    <p class="cours">{matiere}</p>
    <h1>{titre}</h1>
    <p class="accroche">{accroche}</p>
  </header>
{corps}
  <footer class="apercu">
    <h2>Le gabarit {nom}</h2>
    <ul>{puces}</ul>
    <dl class="dosage">{jauges}</dl>
  </footer>
</main>
</body>
</html>
"""


def main() -> None:
    vignettes = []
    for f in FAMILLES:
        (HERE / f"{f[0]}.html").write_text(page(*f), encoding="utf-8")
        vignettes.append(
            f'    <a class="vignette" href="{f[0]}.html"><div class="page"><iframe src="{f[0]}.html" '
            f'title="Aperçu {f[2]}" loading="lazy" scrolling="no" tabindex="-1" aria-hidden="true">'
            f'</iframe></div><span class="nom">{f[2]}</span><span class="ex">{f[4]}</span></a>'
        )
    index = (HERE / "index.html").read_text(encoding="utf-8")
    debut = index.index('  <div class="grille">\n') + len('  <div class="grille">\n')
    fin = index.index("  </div>\n</main>")
    (HERE / "index.html").write_text(index[:debut] + "\n".join(vignettes) + "\n" + index[fin:], encoding="utf-8")
    print(f"{len(FAMILLES)} aperçus construits")


if __name__ == "__main__":
    main()
