# Journal des versions

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
