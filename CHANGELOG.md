# Journal des versions

## Non publié

- Visionneuse Angular des gabarits (`visionneuse/`) : galerie, fiche réelle à côté de la
  description du gabarit, navigation au clavier, largeur ordinateur ou téléphone, thème clair
  ou sombre.
- `apercus/build.py` écrit `apercus/gabarits.json` (familles, dosage, gabarit YAML quand il
  existe) ; les fiches d'aperçu suivent `?theme=` et cachent leur barre dans un cadre.
- Décision 2 proposée (`docs/decisions/02-catalogue-des-blocs-v2.md`) : catalogue des blocs
  v2, quatorze blocs dont trois nouveaux (citation, code, schéma) et deux enrichis (exemple avec
  la règle appliquée, encadré avec les limites), à valider avant d'écrire les sept gabarits.
  Catalogue visible : `apercus/blocs.html` (un exemple de chaque bloc, contenu inventé), rendu
  aussi dans chaque mise en page (`apercus/mep/blocs-*.html`).
- Répertoire des schémas : vingt-trois formes classées par ce qu'il y a à montrer (enchaînement,
  organisation, choix, temps, quantités, comparaison, fonctionnement), chacune dessinée par le
  code (`apercus/dessins.py`) à partir d'une description, avec « montre bien », « à éviter
  quand » et « il faut que le cours dise ». Galerie `apercus/schemas.html`, document engendré
  `docs/schemas/repertoire.md`. Brouillon du moteur de rendu du bloc `schema`.
- Mises en page, second axe des gabarits : trois feuilles de style complètes (Cahier, Poster,
  Cartes) appliquées au même contenu, comparées côte à côte (`apercus/mises-en-page.html`) et
  dans la visionneuse (`/mise-en-page/<id>`). Constat du banc : les neuf gabarits ne se
  distinguaient que par la couleur ; la mise en page est ce qui change la grille, la police,
  la densité et le traitement des blocs.

## 0.2.0 (9 novembre 2026)

- Charte d'écriture (`docs/ecriture.md`) et mesure des tics d'IA (`fiche.ecriture`) ; tirets,
  intervalles, points de suspension et gras corrigés par le code.
- Prompts p2, gabarits v2 : titres qui disent l'idée, « À retenir » et « Teste-toi » en fin de
  chapitre, voix par filière.
- Nouvelle forme de fiche : têtes intégrées, pages en marge, un seul encadré, pièges barrés.
- Mesures de forme au banc : tics pour mille mots, titres en formule, monotonie.

## 0.1.0 (9 novembre 2026)

Premier labo du module fiche de révision.

- Porte d'entrée `fiche.run(FicheRequest) -> Fiche`, contrat de sortie v1 avec schéma JSON
  publié (`docs/schema/fiche-v1.json`). Entrée : le JSON du contrat v1 d'ingest.
- Onze types de blocs : texte, définition, encadré, tableau, étapes, frise, arbre de décision,
  exemple résolu, pièges, essentiel, auto-test. Chaque bloc cite ses passages et ses pages.
- Gabarits YAML versionnés : `sciences-formelles` et `vivant-sante`. Suggestion du gabarit par
  un appel court quand il n'est pas donné.
- Chaîne : plan global, blocs par unité en parallèle, vérification par un petit modèle (blocs
  non soutenus retirés et gardés pour le banc), couverture des notions essentielles.
- Budget par fiche calculé sur les coûts réels, appels abandonnés compris.
- Rendu HTML du labo, CLI (`generer`, `suggerer`, `gabarits`, `rendre`, `schema`,
  `config-example`), tests sans réseau.
- Essai 1 sur deux cours : `docs/banc/2026-11-09-essai1.md`.
