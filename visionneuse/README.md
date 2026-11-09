# Visionneuse des gabarits

Application Angular pour regarder les gabarits de fiche et les corriger. La galerie montre les
neuf fiches d'aperçu ; un clic ouvre un gabarit, avec la fiche réelle au centre et sa
description à droite (intention, dosage, filières, ordre des blocs, règles, blocs permis, ton et
voix, fichiers à modifier).

## Lancer

```bash
uv run python apercus/build.py   # à la racine du dépôt : aperçus et gabarits.json
cd visionneuse
npm install                      # la première fois
npm start                        # http://localhost:4200
```

Angular 21, Node 24 ou plus récent.

## D'où viennent les données

Rien n'est dupliqué ici. Les fiches et `gabarits.json` restent dans `../apercus`, construits par
`apercus/build.py` à partir de `apercus/pages/`, de la liste `FAMILLES` du script et des gabarits
YAML de `src/fiche/familles/`. Avant `npm start`, `build` et `test`,
`scripts/lier-apercus.mjs` crée le lien `visionneuse/apercus -> ../apercus` (une jonction sous
Windows), car Angular ne sert que des fichiers situés dans son dossier.

## Mises en page

Sous la galerie, une seconde section montre **un même cours rendu par plusieurs mises en page**
(Cahier, Poster, Cartes). C'est l'autre axe des gabarits : le gabarit de filière dit quels blocs
la fiche contient, la mise en page dit à quoi ils ressemblent. Chaque mise en page est une
feuille de style complète dans `apercus/mises-en-page/<id>.css`, appliquée au contenu
`apercus/pages/vivant-sante.html` ; la fiche rendue est `apercus/mep/<id>.html`. La route
`/mise-en-page/<id>` l'affiche avec sa description. Pour en ajouter une : une feuille de style,
une entrée dans `MISES_EN_PAGE` (`apercus/build.py`), puis `build.py`.

## Catalogues

Deux pages de référence, liées depuis la galerie et rendues aussi dans chaque mise en page
(`apercus/mep/blocs-*.html`, `apercus/mep/schemas-*.html`) :

- `apercus/blocs.html` : un exemple de chacun des quatorze blocs (décision 2).
- `apercus/schemas.html` : les vingt-trois formes de schémas dessinées par `apercus/dessins.py`,
  avec, pour chacune, ce qu'elle montre bien, quand l'éviter et ce que le cours doit dire.

## Corriger un gabarit

1. Modifier `apercus/pages/<famille>.html` (contenu de la fiche), `apercus/fiche.css` (forme
   commune), `apercus/build.py` (en-tête, dosage) ou `src/fiche/familles/<famille>.yaml`.
2. Relancer `uv run python apercus/build.py`.
3. Cliquer sur ↻ dans la visionneuse (ou laisser le serveur recharger la page).

## Utiliser

- Flèches gauche et droite : gabarit précédent ou suivant ; Échap : retour à la galerie.
- Ordinateur ou Téléphone : largeur de l'aperçu. Auto, Clair, Sombre : thème de la visionneuse
  et des fiches. Ces deux choix sont gardés d'une visite à l'autre.
- ↗ ouvre la fiche seule dans un onglet.

## Code

- `src/app/galerie/` : la grille des vignettes.
- `src/app/detail/` : liste, aperçu, raccourcis clavier.
- `src/app/description/` : le panneau de description d'un gabarit.
- `src/app/partage/` : modèles de `gabarits.json`, lecture du catalogue, préférences, et
  `CadreDirective`, qui charge une fiche dans un cadre sans ajouter d'entrée à l'historique
  (sinon le bouton Retour du navigateur reculerait dans le cadre au lieu de la visionneuse).

Tests : `npm test` (Vitest). Compilation : `npm run build`.
