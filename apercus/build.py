"""Construit les aperçus des gabarits : une page par famille, avec une en-tête et un pied
communs (dosage du gabarit). Le contenu de chaque fiche est écrit à la main dans pages/.

Construit aussi la galerie statique (index.html) et gabarits.json, que lit la visionneuse
Angular (visionneuse/) : pour chaque famille, l'en-tête de l'aperçu, son dosage, et le gabarit
YAML de src/fiche/familles/ quand il existe.

Lancer : uv run python apercus/build.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
import dessins  # noqa: E402  (le répertoire des schémas, à côté de ce script)

FAMILLES_YAML = HERE.parent / "src" / "fiche" / "familles"
# Avant la feuille de style : dans un cadre, la page cache sa barre de navigation, et suit
# le thème demandé par ?theme=light ou ?theme=dark.
INTEGRATION = (
    '<script>(function(){var d=document.documentElement;'
    'if(window.top!==window)d.classList.add("integre");'
    'try{var t=new URLSearchParams(location.search).get("theme");'
    'if(t==="light"||t==="dark")d.dataset.theme=t;}catch(e){}})();</script>'
)
GABARIT_CLES = ("version", "filieres", "pour_etudiant", "ton", "voix", "blocs", "ordre",
                "fin_de_chapitre", "max_blocs_par_section", "max_texte_par_section")
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


# Mises en page : un même contenu, rendu par des feuilles de style complètes et indépendantes.
# C'est l'autre axe des gabarits : le gabarit de filière dit quels blocs, la mise en page dit
# à quoi ils ressemblent. Les prototypes s'appliquent tous au cours de santé (schémas, tableau,
# chiffres, piège). Fichier, nom, polices, description courte, ce qui la caractérise.
MISES_EN_PAGE = [
    ("cahier", "Cahier",
     "https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,700;1,7..72,400&display=swap",
     "Une feuille étroite, du serif, de grandes marges, presque pas de couleur. Pour lire d'un trait.",
     ["Les blocs sont des passages séparés par des filets, pas des cartes.",
      "Les repères de page dans la marge, les tableaux à trois filets comme dans un livre.",
      "L'essentiel entre deux filets doubles, le piège en remarque avec « faux » en petites capitales."]),
    ("poster", "Poster",
     "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap",
     "Deux colonnes denses, chaque bloc dans une boîte titrée, un bandeau de couleur. Tout d'un seul regard.",
     ["Le titre en bandeau plein, la section soulignée d'un trait.",
      "Chaque boîte porte son titre en lettres capitales avec un carré de couleur.",
      "Le piège en boîte d'alerte rouge, l'essentiel en boîte finale sur deux colonnes."]),
    ("cartes", "Cartes",
     "https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&display=swap",
     "Un fond gris et des cartes blanches sur une grille : on pioche dans l'ordre qu'on veut.",
     ["Chaque carte porte une étiquette : schéma, tableau, piège.",
      "Les chiffres en très gros, le piège sur une carte teintée, l'essentiel sur une carte sombre numérotée.",
      "Typographie géométrique, grands titres."]),
]
# Le contenu sur lequel les mises en page sont comparées.
CONTENU_MEP = "vivant-sante"


def squelette(titre_page: str, fontes: str, feuille: str, classe: str, retour: str, nav: str,
              matiere: str, titre: str, accroche: str, corps: str, pied: str, maths: bool) -> str:
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titre_page}</title>
{INTEGRATION}
<link rel="stylesheet" href="{fontes}">
<link rel="stylesheet" href="{feuille}">
{MATHJAX if maths else ""}
</head>
<body class="{classe}">
<main>
  <nav class="haut"><a href="{retour}">{nav}</a><span>Aperçu, contenu inventé</span></nav>
  <header class="titre">
    <p class="cours">{matiere}</p>
    <h1>{titre}</h1>
    <p class="accroche">{accroche}</p>
  </header>
{corps}
  <footer class="apercu">
{pied}
  </footer>
</main>
</body>
</html>
"""


def page(fichier: str, classe: str, nom: str, matiere: str, titre: str, accroche: str,
         dosage: list[int], maths: bool, points: list[str]) -> str:
    corps = (HERE / "pages" / f"{fichier}.html").read_text(encoding="utf-8")
    jauges = "".join(
        f'<dt>{axe}</dt><dd aria-label="{n} sur 5"><i style="width:{n * 20}%"></i></dd>'
        for axe, n in zip(AXES, dosage, strict=True)
    )
    puces = "".join(f"<li>{p}</li>" for p in points)
    pied = f"    <h2>Le gabarit {nom}</h2>\n    <ul>{puces}</ul>\n    <dl class=\"dosage\">{jauges}</dl>"
    return squelette(f"{titre}, gabarit {nom}", FONTS, "fiche.css", classe, "index.html",
                     "Tous les gabarits", matiere, titre, accroche, corps, pied, maths)


def page_mep(mep: tuple[str, str, str, str, list[str]]) -> str:
    """Le contenu de CONTENU_MEP habillé par une mise en page."""
    fichier, nom, fontes, _resume, points = mep
    famille = next(f for f in FAMILLES if f[0] == CONTENU_MEP)
    _f, classe, _nom, matiere, titre, accroche, _dosage, maths, _points = famille
    corps = (HERE / "pages" / f"{CONTENU_MEP}.html").read_text(encoding="utf-8")
    puces = "".join(f"<li>{p}</li>" for p in points)
    pied = f"    <h2>Mise en page {nom}</h2>\n    <ul>{puces}</ul>"
    return squelette(f"{titre}, mise en page {nom}", fontes, f"../mises-en-page/{fichier}.css", classe,
                     "../mises-en-page.html", "Toutes les mises en page", matiere, titre, accroche,
                     corps, pied, maths)


# Les catalogues : un contenu de référence (pages/<fichier>.html), rendu par fiche.css et par
# chaque mise en page. Fichier, matière, titre, accroche, légende du pied, référence.
CATALOGUES = {
    "blocs": ("Catalogue · 14 blocs", "À quoi ressemblent les blocs",
              "Un exemple de chaque bloc du catalogue v2, en contenu inventé, toutes filières mêlées. "
              "Trois sont nouveaux, deux sont enrichis. La même page existe dans chaque mise en page.",
              "Le catalogue des blocs", "Décision 2 : docs/decisions/02-catalogue-des-blocs-v2.md"),
    "schemas": ("Répertoire · 23 formes", "Les schémas que le code sait dessiner",
                "Une forme par question à montrer : un enchaînement, une organisation, un choix, le temps, "
                "des quantités, une comparaison, un fonctionnement. Chaque dessin est produit par le code "
                "à partir d'une description, comme le fera le bloc schéma. Contenus inventés.",
                "Le répertoire des schémas", "Répertoire : docs/schemas/repertoire.md"),
}


def page_catalogue(quoi: str, feuille: str, fontes: str, nom: str, dossier: str) -> str:
    """Un catalogue (pages/<quoi>.html) rendu par une feuille de style."""
    corps = (HERE / "pages" / f"{quoi}.html").read_text(encoding="utf-8")
    matiere, titre, accroche, legende, reference = CATALOGUES[quoi]
    liens = " · ".join(
        [f'<a href="{dossier}{quoi}.html">Fiche</a>']
        + [f'<a href="{dossier}mep/{quoi}-{m[0]}.html">{m[1]}</a>' for m in MISES_EN_PAGE]
    )
    pied = (f"    <h2>{legende}, rendu « {nom} »</h2>\n"
            f"    <p>{reference}. Voir dans une autre forme : {liens}.</p>")
    return squelette(f"{titre}, rendu {nom}", fontes, feuille, "sf", f"{dossier}index.html",
                     "Tous les gabarits", matiere, titre, accroche, corps, pied, True)


def comparaison() -> str:
    """Les mises en page côte à côte, sur le même contenu, pour voir ce qui les distingue."""
    colonnes = "\n".join(
        f'    <section class="mep">\n'
        f'      <a class="feuille" href="mep/{fichier}.html" aria-label="Ouvrir la mise en page {nom}">'
        f'<iframe src="mep/{fichier}.html" title="Mise en page {nom}" loading="lazy" scrolling="no" tabindex="-1" aria-hidden="true"></iframe></a>\n'
        f'      <h2>{nom}</h2>\n      <p>{resume}</p>\n'
        f'      <ul>{"".join(f"<li>{p}</li>" for p in points)}</ul>\n'
        f'      <a class="ouvrir" href="mep/{fichier}.html">Ouvrir en entier</a>\n'
        f'    </section>'
        for fichier, nom, _fontes, resume, points in MISES_EN_PAGE
    )
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mises en page, même contenu</title>
<link rel="stylesheet" href="{FONTS}">
<style>
:root {{ --ground: #f4f5f7; --ink: #1b1d22; --soft: #5a606d; --page: #fff; --accent: #2346b8;
  --head: "Schibsted Grotesk", "Segoe UI", sans-serif; --text: "Atkinson Hyperlegible Next", "Segoe UI", system-ui, sans-serif; color-scheme: light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --ground: #121417; --ink: #e8e9ec; --soft: #a9aebb; --page: #1b1e23; --accent: #93a9ff; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --ground: #121417; --ink: #e8e9ec; --soft: #a9aebb; --page: #1b1e23; --accent: #93a9ff; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--ground); color: var(--ink); font-family: var(--text); font-size: 16px; line-height: 1.5; padding: 40px 16px 64px; }}
main {{ max-width: 1280px; margin: 0 auto; display: grid; gap: 36px; }}
header {{ display: grid; gap: 10px; text-align: center; justify-items: center; }}
h1 {{ font-family: var(--head); font-weight: 800; font-size: clamp(30px, 4.6vw, 44px); letter-spacing: -0.02em; margin: 0; }}
header p {{ color: var(--soft); max-width: 44em; margin: 0; }}
header a {{ color: var(--accent); }}
.grille {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 32px 28px; align-items: start; }}
.mep {{ display: grid; gap: 8px; }}
.feuille {{ position: relative; display: block; aspect-ratio: 3 / 4; border-radius: 10px; overflow: hidden; background: var(--page);
  box-shadow: 0 1px 2px rgba(20, 24, 32, .08), 0 8px 24px rgba(20, 24, 32, .10); }}
.feuille iframe {{ position: absolute; top: 0; left: 0; width: 1000px; height: 1334px; border: 0; transform-origin: 0 0; pointer-events: none; }}
.mep h2 {{ font-family: var(--head); font-weight: 800; font-size: 22px; margin: 8px 0 0; }}
.mep p {{ margin: 0; }}
.mep ul {{ margin: 0; padding-left: 18px; color: var(--soft); font-size: 14.5px; display: grid; gap: 2px; }}
.ouvrir {{ color: var(--accent); font-weight: 700; justify-self: start; }}
</style>
</head>
<body>
<main>
  <header>
    <h1>Un même cours, trois mises en page</h1>
    <p>Le contenu est identique dans les trois colonnes : même titre, mêmes schémas, même tableau, même piège. Seule la feuille de style change. C'est ainsi qu'on voit ce qu'une mise en page apporte. <a href="index.html">Retour aux gabarits</a></p>
  </header>
  <div class="grille">
{colonnes}
  </div>
</main>
<script>
  const fit = () => document.querySelectorAll(".feuille").forEach((p) => {{
    const f = p.querySelector("iframe");
    if (f) f.style.transform = `scale(${{p.clientWidth / 1000}})`;
  }});
  try {{ new ResizeObserver(fit).observe(document.querySelector(".grille")); }} catch (e) {{ window.addEventListener("resize", fit); }}
  fit();
</script>
</body>
</html>
"""


def accent(classe: str) -> str:
    """Couleur de famille en thème clair, lue dans fiche.css."""
    css = (HERE / "fiche.css").read_text(encoding="utf-8")
    trouve = re.search(rf"^body\.{classe} {{ --accent: (#[0-9a-fA-F]{{6}})", css, re.MULTILINE)
    return trouve.group(1) if trouve else "#5a606d"


def gabarit(fichier: str) -> dict[str, object] | None:
    """Le gabarit YAML de la famille s'il est écrit, réduit à ce que la visionneuse montre."""
    chemin = FAMILLES_YAML / f"{fichier}.yaml"
    if not chemin.exists():
        return None
    donnees = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    return {cle: donnees.get(cle) for cle in GABARIT_CLES}


def donnees(f: tuple) -> dict[str, object]:  # type: ignore[type-arg]
    fichier, classe, nom, matiere, titre, accroche, dosage, _maths, points = f
    return {
        "id": fichier, "classe": classe, "nom": nom, "matiere": matiere, "titre": titre,
        "accroche": accroche, "dosage": dosage, "points": points, "accent": accent(classe),
        "gabarit": gabarit(fichier),
    }


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
    (HERE / "mep").mkdir(exist_ok=True)
    for mep in MISES_EN_PAGE:
        (HERE / "mep" / f"{mep[0]}.html").write_text(page_mep(mep), encoding="utf-8")
    (HERE / "mises-en-page.html").write_text(comparaison(), encoding="utf-8")
    (HERE / "pages" / "schemas.html").write_text(dessins.galerie(), encoding="utf-8")
    (HERE.parent / "docs" / "schemas").mkdir(exist_ok=True)
    (HERE.parent / "docs" / "schemas" / "repertoire.md").write_text(dessins.repertoire_markdown(), encoding="utf-8")
    for quoi in CATALOGUES:
        (HERE / f"{quoi}.html").write_text(page_catalogue(quoi, "fiche.css", FONTS, "fiche", ""), encoding="utf-8")
        for fichier, nom, fontes, _resume, _points in MISES_EN_PAGE:
            (HERE / "mep" / f"{quoi}-{fichier}.html").write_text(
                page_catalogue(quoi, f"../mises-en-page/{fichier}.css", fontes, nom, "../"), encoding="utf-8"
            )
    catalogue = {
        "axes": AXES,
        "familles": [donnees(f) for f in FAMILLES],
        "mises_en_page": [
            {"id": m[0], "nom": m[1], "resume": m[3], "points": m[4], "contenu": CONTENU_MEP}
            for m in MISES_EN_PAGE
        ],
    }
    (HERE / "gabarits.json").write_text(
        json.dumps(catalogue, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(f"{len(FAMILLES)} aperçus, {len(MISES_EN_PAGE)} mises en page, gabarits.json à jour")


if __name__ == "__main__":
    main()
