import { computed, signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';

import { CatalogueService } from '../partage/catalogue';
import { AXES, familles } from '../partage/familles.fixture';
import { Detail } from './detail';

describe('Detail', () => {
  let fixture: ComponentFixture<Detail>;
  let navigate: ReturnType<typeof vi.spyOn>;

  function ouvrir(id: string): void {
    fixture = TestBed.createComponent(Detail);
    fixture.componentRef.setInput('id', id);
    fixture.detectChanges();
  }
  const touche = (key: string) => document.dispatchEvent(new KeyboardEvent('keydown', { key }));

  beforeEach(() => {
    const liste = signal(familles());
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: CatalogueService,
          useValue: { statut: signal('pret'), familles: computed(liste), axes: signal(AXES) },
        },
      ],
    });
    navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);
  });

  it('affiche l’aperçu et la description du gabarit demandé', () => {
    ouvrir('beta');
    const el = fixture.nativeElement as HTMLElement;
    expect(el.querySelector('iframe')?.getAttribute('src')).toContain('apercus/beta.html');
    expect(el.querySelector('app-description h2')?.textContent).toContain('Beta');
  });

  it('passe au gabarit suivant ou précédent avec les flèches, en boucle', () => {
    ouvrir('gamma');
    touche('ArrowRight');
    expect(navigate).toHaveBeenLastCalledWith(['/gabarit', 'alpha']);
    touche('ArrowLeft');
    expect(navigate).toHaveBeenLastCalledWith(['/gabarit', 'beta']);
  });

  it('revient à la galerie avec Échap', () => {
    ouvrir('alpha');
    touche('Escape');
    expect(navigate).toHaveBeenLastCalledWith(['/']);
  });

  it('revient à la galerie pour un gabarit inconnu', () => {
    ouvrir('inconnu');
    expect(navigate).toHaveBeenCalledWith(['/']);
  });
});
