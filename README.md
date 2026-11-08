# fiche

Module fiche de révision pour wiliyu, développé à part pour être testé avant intégration. Un
cours structuré par ingest (contrat v1 : passages ancrés, sections, notions) devient une **fiche
en blocs typés** (définitions, encadrés, tableaux, étapes, frises, arbres de décision, exemples
résolus, pièges, essentiel, auto-test), selon un **gabarit de filière** que l'étudiant choisit.

Le modèle remplit un schéma, l'application met en forme. Chaque bloc cite les passages qui le
justifient ; un petit modèle vérifie la fidélité de chaque bloc et retire ceux qu'il ne
soutient pas.

## Installation

```bash
uv sync --group dev
cp .env.example .env      # renseigner MISTRAL_API_KEY
```

## Usage

```bash
uv run fiche gabarits                                    # les gabarits et leur description
uv run fiche generer eval/entrees/mecanique_du_point.json --gabarit sciences-formelles
uv run fiche generer eval/entrees/cours.json             # gabarit suggéré par un appel court
```

La fiche sort en JSON (`out/<cours>.fiche.json`, schéma dans `docs/schema/fiche-v1.json`) et en
HTML (`out/<cours>.fiche.html`) pour la lire et la juger.

En bibliothèque :

```python
from pathlib import Path
from fiche import FicheRequest, run

fiche = run(FicheRequest(course=Path("cours.json"), gabarit="vivant-sante"))
fiche.chapitres[0].sections[0].blocs[0].bloc.type   # "etapes"
fiche.couverture, fiche.usage, fiche.metrics
```

## Chaîne

1. **Unités de rédaction** : les sections feuilles du cours, les plus courtes regroupées
   (moins de 1 500 caractères) pour qu'une diapositive ne coûte pas un appel.
2. **Gabarit** : donné, ou suggéré par un appel court d'après le plan (à confirmer par l'étudiant).
3. **Plan de la fiche** : un appel sur le plan et les notions du cours entier décide, pour chaque
   unité, les blocs à produire et une consigne. C'est ce qui donne un parcours à la fiche.
4. **Blocs** : un appel par unité, en parallèle, qui ne voit que les extraits de l'unité numérotés.
   Validateurs renvoyés au modèle : types permis, extraits existants, formes bien remplies.
5. **Vérification** : un petit modèle relit chaque bloc avec ses extraits ; non soutenu : retiré,
   gardé dans `rejetes` pour le banc.
6. **Assemblage** : blocs par chapitre et section, pages sources, couverture des notions
   essentielles, mesures, coût. Budget vérifié avant chaque appel (`FICHE_MAX_COST_USD`).

## Gabarits

Un fichier YAML par famille dans `src/fiche/familles/` : blocs permis et leur usage, ordre,
densité, ton, consignes pour le plan et pour la rédaction. Les gabarits ne contiennent aucun
exemple tiré d'un cours. Familles présentes : `sciences-formelles`, `vivant-sante`. À venir après
validation sur deux cas : droit et sciences humaines, économie et gestion, informatique et
technique.

## Qualité

`uv run ruff check src tests`, `uv run mypy`, `uv run pytest --cov` (sans réseau, faux modèle).
Décisions dans `docs/decisions/`, journal dans `CHANGELOG.md`.

## Banc

Les entrées (`eval/entrees/*.json`) sont produites par ingest avec la brique notions et ne sont
pas versionnées (textes de cours). Règle de travail : tout changement de prompt ou de gabarit
se valide sur deux cours avant une série. Comptes rendus dans `docs/banc/`.
