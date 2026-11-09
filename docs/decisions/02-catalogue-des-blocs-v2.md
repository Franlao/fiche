# Décision 2 : le catalogue des blocs, version 2

9 novembre 2026. Proposé après les aperçus faits main des neuf gabarits et les trois mises en
page prototypes. À valider par le fondateur.

## Pourquoi on repart des blocs

Tout repose sur eux. Les blocs sont le vocabulaire : ce qu'une fiche peut contenir. Un gabarit
de filière n'est qu'un dosage de ce vocabulaire ; une mise en page n'est qu'une façon de le
dessiner. En composant les neuf aperçus à la main, on a eu besoin de formes qui n'existent pas
dans les onze blocs actuels : un article de loi cité mot pour mot, une citation d'auteur avec
son œuvre, un document d'époque, du code, un cas pratique en trois temps, un schéma. Les
gabarits promettaient donc des choses que la chaîne ne sait pas produire. On complète le
vocabulaire avant d'écrire les sept gabarits manquants.

## Les cinq questions posées à chaque bloc

1. **Usage** : ce que l'étudiant fait avec (apprendre par cœur, comprendre, s'entraîner,
   se vérifier).
2. **Champs** : le minimum pour que le rendu soit fiable et la vérification possible.
3. **Matière** : d'où le modèle la tire dans le cours, et ce que le vérificateur contrôle.
4. **Dessin** : comment chaque mise en page le montre.
5. **Filières** : qui s'en sert, et à quelle fréquence.

Règle commune, inchangée : chaque bloc cite les passages qui le justifient, et le vérificateur
retire ce que les passages ne soutiennent pas.

## Vue d'ensemble

| Bloc | État | Usage principal | Filières où il domine |
|---|---|---|---|
| definition | existe | apprendre par cœur | toutes |
| encadre | **à enrichir** : `limites`, nature `modele` | apprendre par cœur | sciences, économie, droit, psychologie, langues |
| tableau | existe | comparer | toutes |
| etapes | existe | comprendre un mécanisme | santé, informatique, sciences |
| frise | existe | situer dans le temps | histoire, psychologie |
| decision | existe | choisir entre des cas | langues, droit, santé |
| exemple | **à enrichir** : `regle` | s'entraîner | sciences, économie, droit, santé |
| piege | existe | se corriger | toutes |
| essentiel | existe | se vérifier à l'oral | toutes, en fin de chapitre |
| autotest | existe | se vérifier | toutes, en fin de chapitre |
| texte | existe | comprendre, relier | lettres, histoire ; rare ailleurs |
| **citation** | **nouveau** | citer mot pour mot | droit, lettres, histoire, psychologie |
| **code** | **nouveau** | lire et refaire | informatique |
| **schema** | **nouveau** | voir un concept | santé, économie, sciences, informatique |

Quatorze blocs. Trois nouveaux, deux enrichis, neuf inchangés.

## Les blocs un par un

### definition (inchangé)

- **Usage** : apprendre un terme par cœur, avec la notation du cours.
- **Champs** : `titre` (le terme), `definition` (1 à 3 phrases), `exemple` (si le cours en
  donne un, sinon vide).
- **Matière** : la phrase du cours qui définit. Vérification : les mots du cours, pas de
  synonyme qui change le sens.
- **Dessin** : terme en gras suivi de la définition, sur une ligne (Cahier, Poster) ou en
  carte courte (Cartes).
- **Filières** : toutes. Dominant en sciences et en santé ; à plafonner, car le banc a montré
  qu'il envahit la fiche (36 définitions sur 78 blocs en mécanique).

### encadre (à enrichir)

- **Usage** : ce qu'il faut savoir par cœur et savoir citer : théorème, formule, règle, loi,
  principe, et désormais **modèle** ou **théorie**.
- **Champs actuels** : `nature`, `titre`, `enonce`, `conditions`, `variables`, `idee`.
- **Ajouts** :
  - `limites` : liste, les cas où ça ne marche pas ou ce que le cours critique. Vide si le
    cours ne dit rien. Sert au modèle économique (« ajustement pas instantané »), à la théorie
    en psychologie, à la règle de droit et ses exceptions.
  - nature `modele` : hypothèses dans `conditions`, mécanisme dans `idee`, résultat dans
    `enonce`, critiques dans `limites`. C'est la carte en quatre cases de l'aperçu d'économie.
  - nature `date` : pour une date clé isolée en histoire (`enonce` = l'événement, `titre` =
    la date). Évite une frise à un seul repère.
- **Matière** : l'énoncé exact, les hypothèses où le cours les met. Vérification : une
  hypothèse oubliée rend l'énoncé faux, donc non soutenu.
- **Dessin** : carte à fond pâle (gabarits actuels), boîte titrée (Poster), passage entre
  filets (Cahier). Le modèle en quatre cases quand la nature est `modele`.
- **Filières** : sciences formelles, économie, droit, psychologie, langues (la règle de
  grammaire), histoire (la date clé).

### tableau (inchangé)

- **Usage** : comparer des cas sur les mêmes critères, ranger des chiffres.
- **Champs** : `titre`, `colonnes` (2 à 5), `lignes`.
- **Matière** : une énumération ou une comparaison du cours, parfois dispersée sur plusieurs
  passages. Vérification : chaque cellule est dans les passages ; regrouper autrement que le
  texte est permis (leçon de l'essai 1).
- **Dessin** : tableau, à filets ou à lignes teintées selon la mise en page ; défilement
  horizontal sur téléphone.
- **Filières** : toutes. Dominant en langues (formes et marqueurs), psychologie (courants
  comparés), santé (classifications).

### etapes (inchangé)

- **Usage** : comprendre un mécanisme, une méthode, un protocole, dans l'ordre.
- **Champs** : `titre`, `etapes` (2 à 8, chacune `titre` et `detail`).
- **Matière** : un passage qui déroule une suite. Vérification : l'ordre du cours, un acteur
  et un verbe par étape, pas d'étape ajoutée.
- **Dessin** : liste numérotée en gros chiffres ; chaîne de cases fléchées quand il y a moins
  de 6 étapes et que la mise en page le permet (c'est le schéma « du nerf au filament » de
  l'aperçu de santé, qui pourrait être produit par le code à partir d'un bloc `etapes`).
- **Filières** : santé, informatique, sciences (méthode de résolution), économie (mécanisme).

### frise (inchangé)

- **Usage** : situer des repères dans le temps.
- **Champs** : `titre`, `evenements` (3 à 10, chacun `repere` et `evenement`).
- **Matière** : dates et faits du cours. Vérification : chaque date est dans les passages.
- **Dessin** : ligne du temps horizontale, verticale sur téléphone.
- **Filières** : histoire, psychologie (histoire des courants), parfois droit (chronologie
  d'une réforme) et santé (évolution d'une maladie).

### decision (inchangé)

- **Usage** : choisir la bonne réponse selon la situation.
- **Champs** : `titre`, `situation`, `cas` (2 à 6, chacun `si` et `alors`).
- **Matière** : un passage qui distingue des cas. Vérification : tous les cas sont dans le
  cours, aucun cas inventé pour compléter.
- **Dessin** : arbre ou liste « si… alors… ».
- **Filières** : langues (quel temps), droit (quel régime), santé (quelle conduite).

### exemple (à enrichir)

- **Usage** : s'entraîner sur ce que l'examen demandera.
- **Champs actuels** : `titre`, `enonce`, `resolution` (1 à 6 étapes), `resultat`.
- **Ajout** : `regle`, la règle, la formule ou l'outil que l'exemple applique, telle que le
  cours la nomme. Avec ce champ, le bloc devient le **cas pratique** du droit (règle, faits,
  solution), le **cas clinique** de la santé, l'**exemple chiffré** de l'économie, l'**exercice
  résolu** des sciences. Un seul bloc pour quatre usages, dessiné selon la filière.
- **Matière** : un exemple ou un exercice que le cours résout lui-même. Vérification : la
  plus stricte de toutes, le banc a montré que le modèle invente des exemples résolus (6
  retirés en mécanique). Si le cours ne résout pas, pas de bloc.
- **Dessin** : énoncé, puis la règle en évidence, puis les étapes, puis ce qu'on retient. En
  droit, les trois temps « la règle, les faits, la solution » de l'aperçu.
- **Filières** : sciences, économie, droit, santé, informatique.

### piege (inchangé)

- **Usage** : se corriger d'une confusion fréquente.
- **Champs** : `titre`, `pieges` (1 à 5, chacun `erreur` et `correction`).
- **Matière** : deux éléments proches du cours, ou une erreur que le cours signale lui-même.
  Vérification : les deux côtés sont dans les passages.
- **Dessin** : l'idée reçue puis la correction. La bulle « Ce qu'on entend en TD » des
  aperçus est une mise en forme, pas un champ.
- **Filières** : toutes.

### essentiel (inchangé)

- **Usage** : se vérifier à l'oral, redire le chapitre sans la fiche.
- **Champs** : `titre`, `points` (3 à 8 phrases complètes).
- **Matière** : le chapitre entier. Vérification : c'est le bloc le plus rejeté du banc (9
  rejets sur 23), parce qu'il généralise. Consigne : seulement ce que les passages disent.
- **Dessin** : la carte la plus visible de la partie, quelle que soit la mise en page.
- **Filières** : toutes, obligatoire en fin de chapitre.

### autotest (inchangé)

- **Usage** : se vérifier par des questions.
- **Champs** : `titre`, `questions` (2 à 4, chacune `question` et `reponse`).
- **Matière** : le chapitre. Vérification : la réponse est dans les passages.
- **À faire** : la forme des questions doit suivre l'épreuve de la filière (calcul, cas,
  question de cours, phrase à produire). C'est le gabarit qui le dira, par un champ `epreuve`
  (décision à venir sur les gabarits).
- **Dessin** : questions dépliables.
- **Filières** : toutes, obligatoire en fin de chapitre.

### texte (inchangé)

- **Usage** : comprendre une idée qui relie, poser une problématique, raconter un
  enchaînement.
- **Champs** : `titre`, `contenu` (2 à 4 phrases).
- **Matière** : un passage de raisonnement. Vérification : pas de généralisation.
- **Dessin** : paragraphe.
- **Filières** : lettres et histoire, où il est la forme principale (dosage « texte rédigé » à
  5 et 4) ; rare et plafonné ailleurs.

### citation (nouveau)

- **Usage** : citer mot pour mot ce que l'examen exige de citer : un article de loi, une
  phrase d'auteur, un document d'époque, une expérience fondatrice.
- **Champs** : `nature` (`article`, `citation`, `document`, `experience`), `texte` (la
  citation exacte, entre guillemets au rendu), `reference` (article 1128 du Code civil ;
  Descartes, *Discours de la méthode*, 1637 ; Sieyès, pamphlet, janvier 1789 ; Pavlov, 1890),
  `portee` (ce qu'on en tire, 1 ou 2 phrases, vide si le cours ne commente pas).
- **Matière** : le texte cité tel qu'il est dans le cours. Vérification : **exacte au mot
  près**, c'est la seule vérification littérale de toute la chaîne. Une citation retouchée
  est non soutenue. La référence doit être dans les passages aussi.
- **Dessin** : carte à part avec le texte en plus grand et la référence en petit (gabarits
  actuels), passage entre guillemets avec référence en marge (Cahier), boîte « à citer »
  (Poster).
- **Filières** : droit (dosage « citations » à 5), lettres (5), histoire (3), psychologie
  (2). Absent ailleurs.
- **Pourquoi un bloc et pas un encadré** : l'encadré reformule, la citation cite. Le
  vérificateur ne contrôle pas la même chose, et l'étudiant n'en fait pas le même usage.
- **Pourquoi « citation » et pas « source »** : « source » désigne déjà, partout dans la
  chaîne, les passages du cours dont un bloc est tiré (`passages`, `_sources` dans le rendu).
  Le bloc, lui, est un contenu que l'étudiant apprend. Deux mots pour deux choses.

### code (nouveau)

- **Usage** : lire un algorithme, le refaire, en suivre l'exécution.
- **Champs** : `titre`, `langage` (pseudo-code, Python, SQL…), `lignes` (liste de chaînes,
  une par ligne, indentation conservée), `commentaires` (liste de paires `ligne`, `texte` :
  ce que fait telle ligne, vide si le cours ne l'explique pas), `trace` (facultatif : un
  tableau d'exécution sur un exemple, colonnes et lignes, si le cours le donne).
- **Matière** : le code du cours. Vérification : les lignes sont celles du cours, à
  l'indentation près ; aucune ligne ajoutée, aucune « correction » du code du professeur.
- **Dessin** : bloc monospace à lignes numérotées, mots-clés en couleur ; la trace en tableau
  dessous. Sur téléphone, défilement horizontal.
- **Filières** : informatique et technique. Sans ce bloc, le gabarit n'a pas de sens : le
  dosage « formules ou code » y est à 5.

### schema (nouveau)

- **Usage** : voir un concept qu'un texte explique mal : une chaîne, une courbe, une
  organisation, une structure.
- **Le principe** : le modèle ne dessine pas, il décrit. Il remplit une structure, le code la
  rend. Comme pour le reste de la fiche, chaque étiquette et chaque valeur est vérifiable dans
  les passages. Quatre formes, selon ce qu'il y a à montrer :

| Forme | Exemples | Qui dessine | Ce que le modèle fournit |
|---|---|---|---|
| `diagramme` | chaîne, cycle, arbre, grille (le cycle de l'eau du catalogue) | le code, en SVG | `disposition`, `noeuds`, `liens` |
| `graphique` | courbes, barres, boîtes à moustaches, violons ; la courbe offre-demande | le code, par une spécification Vega-Lite validée | `type`, `donnees` si le cours les donne, sinon `allure` (« décroissante », « se croisent en E »), axes et unités |
| `illustration` | un schéma explicatif fait de pictogrammes, de zones, de flèches et de légendes | le code, avec une bibliothèque de pictogrammes nommés (personne, écran, livre, outil, horloge…) | `elements` (pictogramme, étiquette, position), `fleches`, `zones` |
| `image` | une cellule, un cœur, un muscle, une coupe, une carte | personne : on reprend l'image du PDF | `image_id`, `page` |

- **Champs communs** : `titre`, `forme`, `legende` (1 ou 2 phrases du cours).
- **Matière et vérification** : diagramme, chaque nœud et chaque lien nommés dans les
  passages ; graphique, les données ou l'allure décrites par le cours, les unités exactes ;
  illustration, chaque étiquette dans les passages, les pictogrammes limités à la bibliothèque ;
  image, la légende d'origine.
- **Ce qui est hors de portée du code** : seule la forme `image`. Elle dépend d'ingest, dont le
  contrat v1 ne transporte que du texte : il faudra qu'il extraie les images avec leur page et
  leur légende.
- **Images générées par un modèle** : écartées. Une anatomie fausse dans une fiche de médecine
  est pire que pas d'image, et rien ne peut la vérifier.
- **Dessin** : pleine largeur, légende dessous. À régler : la lisibilité sur téléphone, où les
  aperçus actuels tombent à 7 pixels de texte ; les étiquettes ne doivent pas rétrécir avec le
  dessin.
- **Filières** : santé (dosage « illustrations » à 5), économie (4), informatique (3),
  psychologie (3), histoire (3), sciences (2).
- **Ordre** : diagramme (déjà prototypé), puis graphique (Vega-Lite est fait pour ça), puis
  illustration (une bibliothèque courte, une vingtaine de pictogrammes, trois dispositions),
  puis image (demande à ingest).

## Ce que ça change ailleurs

- **Schéma JSON et modèles Pydantic** : trois types de plus, deux champs de plus, deux
  natures de plus. Version du schéma : 2.
- **Prompts** : le prompt des blocs décrit chaque forme ; les trois nouvelles s'ajoutent. Le
  vérificateur reçoit une consigne littérale pour `citation` et `code`.
- **Rendu** : une forme par bloc et par mise en page. Le dessin des `etapes` en chaîne fléchée
  et des `decision` en arbre est un gain gratuit.
- **Gabarits** : les sept manquants peuvent alors être écrits à partir des aperçus. Ils
  gagneront un champ `epreuve` et une contrainte de variété (décision 3, à venir).
- **Ingest** : demande d'extraction des images avec page et légende, pour la voie 1 du
  schéma. Hors de ce dépôt.

## Ordre de réalisation proposé

1. `citation` et `exemple.regle` : ils débloquent droit, lettres, histoire, psychologie.
2. `code` : il débloque informatique.
3. `encadre.limites` et nature `modele` : économie et psychologie.
4. `schema` : diagramme, puis graphique, puis illustration ; demande à ingest pour la forme `image`.
5. Les sept gabarits, deux par deux, validés sur deux cours chacun.

## Signal de réexamen

Si, sur deux cours de droit, le bloc `citation` est rejeté à plus de 15 % pour inexactitude
littérale, c'est que le modèle ne sait pas copier mot pour mot : il faudra alors extraire les
citations par le code (recherche du passage) plutôt que par le modèle.
