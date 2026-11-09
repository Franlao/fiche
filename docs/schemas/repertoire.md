# Répertoire des schémas

Engendré par `apercus/build.py` depuis `apercus/dessins.py` : ne pas modifier à la main.
La galerie dessinée est `apercus/schemas.html`, et dans chaque mise en page `apercus/mep/schemas-*.html`.

Le bloc `schema` (décision 2) choisit une forme d'après **ce qu'il y a à montrer**, pas par
habitude. Pour chaque forme : ce qu'elle montre bien, quand ne pas l'utiliser, ce que le cours
doit dire pour qu'on ait le droit de s'en servir, et les champs que le modèle remplit. Le code
dessine ; le modèle décrit. Chaque forme de ce répertoire est dessinée par `dessins.py`, donc
dessinable.

Trois garde-fous contre la répétition : le plan justifie son choix (`pourquoi_cette_forme`),
le gabarit interdit de reprendre une forme dans le même chapitre si une autre convient, et le
banc mesure la diversité des formes par fiche.

| # | Forme | Pour montrer | Champs |
|---|---|---|---|
| 1 | Chaîne d'étapes | un enchaînement | `etapes (3 à 6), liens (facultatif, un par flèche)` |
| 2 | Cycle | un enchaînement | `etapes (4), centre (facultatif)` |
| 3 | Boucle de rétroaction | un enchaînement | `etapes (2 à 4), retour (ce que fait le retour), signe (+ ou −)` |
| 4 | Escalier | un enchaînement | `etapes (3 à 5)` |
| 5 | Couloirs | un enchaînement | `acteurs (2 à 4), etapes (acteur, texte)` |
| 6 | Hiérarchie | une organisation | `racine, enfants (2 à 4), petits-enfants (facultatif)` |
| 7 | Ensembles | une organisation | `a, b, inter, seul_a, seul_b` |
| 8 | Carte mentale | une organisation | `centre, branches (4, chacune avec 2 à 3 sous-points)` |
| 9 | Matrice deux par deux | une organisation | `axe_x (deux valeurs), axe_y (deux valeurs), cases (4)` |
| 10 | Pyramide | une organisation | `niveaux (3 à 6, du sommet à la base)` |
| 11 | Arbre de décision | un choix | `question, branches (condition, résultat) × 2 ou 3` |
| 12 | Frise | le temps | `reperes (date, événement) × 3 à 8` |
| 13 | Périodes | le temps | `bandes (nom, début, fin), échelle (min, max, unité)` |
| 14 | Avant et après | le temps | `avant (titre, lignes), apres (titre, lignes)` |
| 15 | Barres | des quantités | `categories, valeurs, unite` |
| 16 | Courbe | des quantités | `points ou allure, phases (début, fin, nom), axe_x, axe_y` |
| 17 | Boîtes à moustaches | des quantités | `groupes (nom, min, Q1, médiane, Q3, max), axe` |
| 18 | Nuage de points | des quantités | `points (x, y), axe_x, axe_y, tendance` |
| 19 | Jauge | des quantités | `min, max, plage, unite, reperes (valeur, nom), valeur_label` |
| 20 | Face à face | une comparaison | `gauche (titre, valeurs), droite (titre, valeurs), criteres` |
| 21 | Grille de chaleur | une comparaison | `lignes, colonnes, niveaux (1 à 3), legende` |
| 22 | Illustration à pictogrammes | un fonctionnement | `elements (pictogramme, étiquette, position), fleches (de, vers, étiquette), zones` |
| 23 | Coupe à zones | un fonctionnement | `zones (nom, épaisseur relative, détail)` |

## Pour montrer un enchaînement

### 1. Chaîne d'étapes

- **Montre bien** : une suite ordonnée de 3 à 6 étapes, chacune déclenchant la suivante.
- **À éviter quand** : les étapes sont plus de six (faire deux chaînes), ou le cours ne donne pas d'ordre.
- **Il faut que le cours dise** : l'ordre des étapes et, s'il y en a, ce qui passe de l'une à l'autre.
- **Champs** : `etapes (3 à 6), liens (facultatif, un par flèche)`
- **Exemple de la galerie** : De la lumière au sucre : les quatre temps de la photosynthèse tels que le cours les nomme.
- **Autres cas** : un protocole, une chaîne de production, une réaction en étapes.

### 2. Cycle

- **Montre bien** : quatre étapes dont la dernière relance la première.
- **À éviter quand** : la fin ne relance pas le début : c'est une chaîne, pas un cycle.
- **Il faut que le cours dise** : que le cours dise explicitement que ça recommence.
- **Champs** : `etapes (4), centre (facultatif)`
- **Exemple de la galerie** : Le cycle économique : chaque phase prépare la suivante, et la reprise ramène à l'expansion.
- **Autres cas** : cycle de l'eau, cycle cellulaire, cycle de vie d'un produit.

### 3. Boucle de rétroaction

- **Montre bien** : un effet qui revient sur sa cause pour la freiner (−) ou l'amplifier (+).
- **À éviter quand** : le retour n'est pas dans le cours : ne pas l'inventer pour faire joli.
- **Il faut que le cours dise** : la cause, l'effet, et le sens du retour.
- **Champs** : `etapes (2 à 4), retour (ce que fait le retour), signe (+ ou −)`
- **Exemple de la galerie** : La glycémie : l'insuline fait baisser le sucre, ce qui freine la sécrétion d'insuline.
- **Autres cas** : thermostat, offre et prix, emballement d'une rumeur.

### 4. Escalier

- **Montre bien** : des étapes qui s'ajoutent les unes aux autres, chacune supposant la précédente acquise.
- **À éviter quand** : les étapes sont indépendantes : une chaîne suffit.
- **Il faut que le cours dise** : que chaque étape s'appuie sur la précédente.
- **Champs** : `etapes (3 à 5)`
- **Exemple de la galerie** : Les recours contre une décision : on ne saute pas une marche.
- **Autres cas** : niveaux de preuve, paliers d'apprentissage, degrés de juridiction.

### 5. Couloirs

- **Montre bien** : qui fait quoi quand plusieurs acteurs se passent le relais.
- **À éviter quand** : il n'y a qu'un acteur : une chaîne suffit.
- **Il faut que le cours dise** : les acteurs et l'étape dont chacun est responsable.
- **Champs** : `acteurs (2 à 4), etapes (acteur, texte)`
- **Exemple de la galerie** : Une commande en ligne : trois acteurs, cinq étapes, le relais passe de l'un à l'autre.
- **Autres cas** : circuit d'une ordonnance, procédure législative, traitement d'une demande.

## Pour montrer une organisation

### 6. Hiérarchie

- **Montre bien** : ce qui dépend de quoi : un tout et ses parties, un chef et ses services.
- **À éviter quand** : les éléments sont au même niveau : un tableau ou une carte mentale.
- **Il faut que le cours dise** : le lien de dépendance entre les niveaux.
- **Champs** : `racine, enfants (2 à 4), petits-enfants (facultatif)`
- **Exemple de la galerie** : Les trois pouvoirs et ce qu'ils font, sous la Constitution.
- **Autres cas** : classification du vivant, organigramme, arborescence de fichiers.

### 7. Ensembles

- **Montre bien** : deux notions qui se recouvrent en partie : ce qui est propre à chacune, ce qui est commun.
- **À éviter quand** : les deux notions ne se recouvrent pas : un face-à-face.
- **Il faut que le cours dise** : les trois zones : A seul, B seul, commun.
- **Champs** : `a, b, inter, seul_a, seul_b`
- **Exemple de la galerie** : Carré, rectangle, losange : le carré est à l'intersection.
- **Autres cas** : sciences et techniques, droit public et privé, deux maladies aux symptômes communs.

### 8. Carte mentale

- **Montre bien** : un sujet central et ses quatre facettes, chacune avec deux ou trois mots.
- **À éviter quand** : il y a un ordre entre les branches : une chaîne ou un arbre.
- **Il faut que le cours dise** : que les branches soient bien des facettes du même sujet, pas des étapes.
- **Champs** : `centre, branches (4, chacune avec 2 à 3 sous-points)`
- **Exemple de la galerie** : La cellule vue sous quatre angles, pour réviser d'un coup d'œil.
- **Autres cas** : un auteur et ses thèmes, une période et ses aspects, un concept et ses usages.

### 9. Matrice deux par deux

- **Montre bien** : quatre situations définies par deux critères qui ont chacun deux valeurs.
- **À éviter quand** : les critères ont plus de deux valeurs : une grille.
- **Il faut que le cours dise** : les deux critères et ce que le cours met dans chaque case.
- **Champs** : `axe_x (deux valeurs), axe_y (deux valeurs), cases (4)`
- **Exemple de la galerie** : Classer les tâches par urgence et importance : la matrice du cours de gestion.
- **Autres cas** : BCG, risque et rendement, public et privé croisé avec national et local.

### 10. Pyramide

- **Montre bien** : des niveaux ordonnés du plus fondamental (en bas) au plus élevé, ou du plus nombreux au plus rare.
- **À éviter quand** : il n'y a pas d'ordre entre les niveaux.
- **Il faut que le cours dise** : l'ordre des niveaux et ce qui le fonde.
- **Champs** : `niveaux (3 à 6, du sommet à la base)`
- **Exemple de la galerie** : La hiérarchie des normes : chaque étage doit respecter celui du dessus.
- **Autres cas** : pyramide des âges, chaîne alimentaire, besoins.

## Pour montrer un choix

### 11. Arbre de décision

- **Montre bien** : une question et la réponse selon le cas.
- **À éviter quand** : il y a plus de trois cas ou des cas emboîtés : le bloc decision en liste.
- **Il faut que le cours dise** : tous les cas que le cours distingue, aucun ajouté.
- **Champs** : `question, branches (condition, résultat) × 2 ou 3`
- **Exemple de la galerie** : Quel temps en anglais ? La question que pose le cours, et ses trois réponses.
- **Autres cas** : quel régime juridique, quelle conduite devant un symptôme, quel algorithme.

## Pour montrer le temps

### 12. Frise

- **Montre bien** : des événements datés, dans l'ordre, sur une ligne.
- **À éviter quand** : les événements durent : des périodes.
- **Il faut que le cours dise** : les dates exactes du cours.
- **Champs** : `reperes (date, événement) × 3 à 8`
- **Exemple de la galerie** : Un siècle de régimes politiques en cinq dates.
- **Autres cas** : étapes d'une découverte, vie d'un auteur, chronologie d'une réforme.

### 13. Périodes

- **Montre bien** : des phases qui durent, avec leur début et leur fin, parfois qui se chevauchent.
- **À éviter quand** : ce sont des instants : une frise.
- **Il faut que le cours dise** : les bornes de chaque période.
- **Champs** : `bandes (nom, début, fin), échelle (min, max, unité)`
- **Exemple de la galerie** : Les stades du développement selon le cours de psychologie, en années.
- **Autres cas** : ères géologiques, phases d'un projet, règnes.

### 14. Avant et après

- **Montre bien** : ce qui change entre deux états, point par point.
- **À éviter quand** : il y a plus de deux états : une chaîne.
- **Il faut que le cours dise** : les deux états décrits par le cours, sur les mêmes points.
- **Champs** : `avant (titre, lignes), apres (titre, lignes)`
- **Exemple de la galerie** : La mitose : une cellule avant, deux cellules identiques après.
- **Autres cas** : une réforme, une réaction chimique, une transformation économique.

## Pour montrer des quantités

### 15. Barres

- **Montre bien** : comparer quelques valeurs entre catégories.
- **À éviter quand** : il y a plus de huit catégories, ou les valeurs ne sont pas dans le cours.
- **Il faut que le cours dise** : les valeurs exactes et leur unité.
- **Champs** : `categories, valeurs, unite`
- **Exemple de la galerie** : La composition de l'air : trois chiffres que le cours donne.
- **Autres cas** : répartition d'un budget, effectifs, résultats d'une expérience.

### 16. Courbe

- **Montre bien** : une évolution continue, avec ses phases ; la forme compte plus que les valeurs.
- **À éviter quand** : le cours ne décrit ni valeurs ni allure.
- **Il faut que le cours dise** : soit des points, soit l'allure (croît, plafonne, décroît) et le nom des phases.
- **Champs** : `points ou allure, phases (début, fin, nom), axe_x, axe_y`
- **Exemple de la galerie** : Une population de bactéries : les quatre phases que le cours nomme, sans chiffres.
- **Autres cas** : offre et demande, courbe de Phillips, cinétique d'une réaction.

### 17. Boîtes à moustaches

- **Montre bien** : la dispersion de plusieurs groupes : médiane, quartiles, extrêmes.
- **À éviter quand** : le cours ne donne que des moyennes : des barres.
- **Il faut que le cours dise** : les cinq valeurs par groupe, ou les données brutes.
- **Champs** : `groupes (nom, min, Q1, médiane, Q3, max), axe`
- **Exemple de la galerie** : Les notes de deux groupes : même médiane, dispersion différente.
- **Autres cas** : mesures répétées, salaires par secteur, tailles par espèce.

### 18. Nuage de points

- **Montre bien** : le lien entre deux grandeurs mesurées sur les mêmes individus.
- **À éviter quand** : il y a moins de six points, ou pas de lien à montrer.
- **Il faut que le cours dise** : les couples de valeurs du cours.
- **Champs** : `points (x, y), axe_x, axe_y, tendance`
- **Exemple de la galerie** : Taille et masse : les points montent ensemble, la droite résume la tendance.
- **Autres cas** : revenu et consommation, dose et effet, heures de révision et note.

### 19. Jauge

- **Montre bien** : une valeur ou une plage normale sur son échelle, avec des seuils.
- **À éviter quand** : il y a plusieurs valeurs à comparer : des barres.
- **Il faut que le cours dise** : la plage, l'échelle et les seuils donnés par le cours.
- **Champs** : `min, max, plage, unite, reperes (valeur, nom), valeur_label`
- **Exemple de la galerie** : Le pH du sang : une plage étroite, deux seuils de danger.
- **Autres cas** : température corporelle, taux légal, seuil de pauvreté.

## Pour montrer une comparaison

### 20. Face à face

- **Montre bien** : deux notions comparées critère par critère.
- **À éviter quand** : il y a plus de deux notions : un tableau.
- **Il faut que le cours dise** : les critères et les deux valeurs pour chacun.
- **Champs** : `gauche (titre, valeurs), droite (titre, valeurs), criteres`
- **Exemple de la galerie** : Mitose et méiose, sur quatre critères du cours.
- **Autres cas** : deux auteurs, deux régimes, deux algorithmes.

### 21. Grille de chaleur

- **Montre bien** : un niveau (faible, moyen, fort) au croisement de deux critères.
- **À éviter quand** : les cases contiennent du texte long : un tableau.
- **Il faut que le cours dise** : le niveau de chaque case, tel que le cours le qualifie.
- **Champs** : `lignes, colonnes, niveaux (1 à 3), legende`
- **Exemple de la galerie** : Le risque selon la probabilité et la gravité : la grille du cours de gestion.
- **Autres cas** : compatibilités, fréquence de symptômes, matrice de confusion.

## Pour montrer un fonctionnement

### 22. Illustration à pictogrammes

- **Montre bien** : qui échange quoi avec qui : des acteurs, des objets, des flux.
- **À éviter quand** : il n'y a pas d'acteurs distincts : un diagramme suffit.
- **Il faut que le cours dise** : les acteurs, les objets et le sens des échanges ; les pictogrammes viennent de la bibliothèque, jamais inventés.
- **Champs** : `elements (pictogramme, étiquette, position), fleches (de, vers, étiquette), zones`
- **Exemple de la galerie** : Le circuit d'une ordonnance : le médecin, le patient, la pharmacie, l'assurance.
- **Autres cas** : un marché, une procédure, une chaîne logistique.

### 23. Coupe à zones

- **Montre bien** : des couches superposées, chacune avec son nom et son rôle.
- **À éviter quand** : la structure n'est pas en couches : c'est une image du cours.
- **Il faut que le cours dise** : l'ordre des couches et ce que le cours dit de chacune.
- **Champs** : `zones (nom, épaisseur relative, détail)`
- **Exemple de la galerie** : Les trois couches de la peau, de la surface à la profondeur.
- **Autres cas** : couches de l'atmosphère, strates géologiques, couches réseau.

## Formes à l'étude

- **Balance** (peser deux séries d'arguments) : proche du face-à-face, à ajouter si un cours
  en a besoin.
- **Carte à zones** (un lieu) : le dessin de contours fidèles n'est pas à la portée du code ;
  c'est la forme `image` du bloc.
- **Image du cours** : la seule forme qui n'est pas dessinée ; elle dépend d'ingest.
