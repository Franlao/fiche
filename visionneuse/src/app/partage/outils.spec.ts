import { LibelleBlocPipe, lienApercu } from './outils';

describe('lienApercu', () => {
  it('pointe vers la fiche sans paramètre en thème automatique', () => {
    expect(lienApercu('droit', 'auto')).toBe('apercus/droit.html');
  });

  it('transmet le thème et le compteur de rechargement', () => {
    expect(lienApercu('droit', 'dark', 3)).toBe('apercus/droit.html?theme=dark&r=3');
  });

  it('pointe vers le sous-dossier des mises en page quand on le lui donne', () => {
    expect(lienApercu('cahier', 'auto', 0, 'mep/')).toBe('apercus/mep/cahier.html');
  });
});

describe('LibelleBlocPipe', () => {
  const pipe = new LibelleBlocPipe();

  it('donne le nom lu par l’étudiant', () => {
    expect(pipe.transform('decision')).toBe('Arbre de décision');
  });

  it('garde un type inconnu tel quel', () => {
    expect(pipe.transform('nouveau')).toBe('nouveau');
  });
});
