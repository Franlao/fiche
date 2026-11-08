# Décision 1 : labo séparé, blocs typés, gabarit suggéré puis confirmé

9 novembre 2026, décidé par le fondateur sur la proposition du schéma « Module fiche de révision ».

## Ce qui est décidé

| Question | Choix | Alternative écartée | Raison |
|---|---|---|---|
| Où construire | Labo séparé, comme ingest. Entrée : le JSON du contrat v1 d'ingest | Directement dans le worker wiliyu | Itérer sur les prompts et les gabarits sans toucher la production ; intégration quand le banc convainc |
| Forme de la fiche | Blocs typés que l'application met en forme | Markdown libre | On peut vérifier, ancrer et compter bloc par bloc, et garantir qu'un tableau est un tableau |
| Choix du gabarit | Suggéré par un appel court, confirmé par l'étudiant | Choix par l'étudiant seul | L'étudiant ne sait pas toujours quelle famille convient à un cours transversal ; la suggestion coûte moins d'un centime |
| Budget | 0,50 $ par fiche (`FICHE_MAX_COST_USD`), sections restantes en « budget » au-delà | Arrêt de la fiche | Même règle que le plafond de wiliyu : une fiche partielle vaut mieux que pas de fiche |

## Chaîne retenue

Unités de rédaction (sections feuilles, les courtes regroupées), plan global en un appel,
blocs par unité en parallèle, vérification de chaque bloc par un petit modèle, couverture des
notions essentielles, assemblage. Détail dans le README.

## Signal de réexamen

Taux de rejet par la vérification au-dessus de 15 % (critère repris de wiliyu) sur la série
complète, ou fiche jugée « cours allégé » à la lecture : revoir le prompt des blocs et le
gabarit avant d'élargir.
