import { Famille } from './modeles';

export const AXES = [
  'Illustrations',
  'Tableaux',
  'Texte rédigé',
  'Formules ou code',
  'Citations et sources',
];

/** Trois familles inventées pour les tests, dont une seule avec son gabarit YAML. */
export function familles(): Famille[] {
  const base = {
    classe: 'x',
    matiere: 'Matière · L1',
    titre: 'Titre',
    accroche: 'Accroche.',
    dosage: [1, 2, 3, 4, 5],
    points: ['Un point.'],
    accent: '#123456',
    gabarit: null,
  };
  return [
    {
      ...base,
      id: 'alpha',
      nom: 'Alpha',
      gabarit: {
        version: 2,
        filieres: ['biologie'],
        pour_etudiant: 'Les mécanismes en étapes.',
        ton: 'Direct.',
        voix: null,
        blocs: [{ type: 'decision', usage: 'Quand le cours distingue des cas.' }],
        ordre: ['texte', 'decision'],
        fin_de_chapitre: ['essentiel', 'autotest'],
        max_blocs_par_section: 7,
        max_texte_par_section: 1,
      },
    },
    { ...base, id: 'beta', nom: 'Beta' },
    { ...base, id: 'gamma', nom: 'Gamma' },
  ];
}
