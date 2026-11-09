/** Forme de apercus/gabarits.json, écrit par apercus/build.py. */

export interface BlocUsage {
  type: string;
  usage: string;
}

/** Le gabarit YAML de src/fiche/familles/, réduit à ce que la visionneuse montre. */
export interface Gabarit {
  version: number | null;
  filieres: string[] | null;
  pour_etudiant: string | null;
  ton: string | null;
  voix: string | null;
  blocs: BlocUsage[] | null;
  ordre: string[] | null;
  fin_de_chapitre: string[] | null;
  max_blocs_par_section: number | null;
  max_texte_par_section: number | null;
}

export interface Famille {
  id: string;
  classe: string;
  nom: string;
  matiere: string;
  titre: string;
  accroche: string;
  /** De 0 à 5, un nombre par axe du catalogue. */
  dosage: number[];
  points: string[];
  /** Couleur de famille en thème clair, lue dans fiche.css. */
  accent: string;
  /** Absent tant que le fichier YAML de la famille n'est pas écrit. */
  gabarit: Gabarit | null;
}

/**
 * Une mise en page : une feuille de style complète (apercus/mises-en-page/<id>.css) appliquée à
 * un même contenu. L'autre axe des gabarits : le gabarit dit quels blocs, la mise en page dit
 * à quoi ils ressemblent. La fiche rendue est apercus/mep/<id>.html.
 */
export interface MiseEnPage {
  id: string;
  nom: string;
  resume: string;
  points: string[];
  /** Identifiant de la famille dont le contenu sert de banc d'essai. */
  contenu: string;
}

export interface Catalogue {
  axes: string[];
  familles: Famille[];
  mises_en_page: MiseEnPage[];
}
