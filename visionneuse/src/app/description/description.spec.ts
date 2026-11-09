import { TestBed } from '@angular/core/testing';

import { AXES, familles } from '../partage/familles.fixture';
import { Famille } from '../partage/modeles';
import { Description } from './description';

function rendre(famille: Famille): HTMLElement {
  const fixture = TestBed.createComponent(Description);
  fixture.componentRef.setInput('famille', famille);
  fixture.componentRef.setInput('axes', AXES);
  fixture.detectChanges();
  return fixture.nativeElement as HTMLElement;
}

describe('Description', () => {
  it('montre les blocs permis et les règles d’un gabarit écrit', () => {
    const el = rendre(familles()[0]);
    expect(el.textContent).toContain('Les mécanismes en étapes.');
    expect(el.querySelector('.blocs')?.textContent).toContain('Arbre de décision');
    expect(el.textContent).toContain("En fin de chapitre : L'essentiel, Teste-toi");
    expect(el.querySelector('.manque')).toBeNull();
  });

  it('signale un gabarit pas encore écrit', () => {
    const el = rendre(familles()[1]);
    expect(el.querySelector('.manque')).not.toBeNull();
    expect(el.textContent).toContain('src/fiche/familles/beta.yaml (à écrire)');
  });

  it('trace une jauge par axe du dosage', () => {
    const jauges = rendre(familles()[0]).querySelectorAll<HTMLElement>('.dosage dd i');
    expect(jauges.length).toBe(5);
    expect(jauges[2].style.width).toBe('60%');
  });
});
