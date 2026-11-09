import { HttpClient } from '@angular/common/http';
import { computed, inject, Injectable } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of } from 'rxjs';

import { Catalogue, Famille, MiseEnPage } from './modeles';

/** Servi depuis le lien visionneuse/apercus -> ../apercus (scripts/lier-apercus.mjs, angular.json). */
export const CATALOGUE_URL = 'apercus/gabarits.json';

type Etat =
  { statut: 'chargement' } | { statut: 'erreur' } | { statut: 'pret'; catalogue: Catalogue };

/** Les familles, leur gabarit et les mises en page, lus une fois au démarrage. */
@Injectable({ providedIn: 'root' })
export class CatalogueService {
  private readonly etat = toSignal(
    inject(HttpClient)
      .get<Catalogue>(CATALOGUE_URL)
      .pipe(
        map((catalogue): Etat => ({ statut: 'pret', catalogue })),
        catchError(() => of<Etat>({ statut: 'erreur' })),
      ),
    { initialValue: { statut: 'chargement' } as Etat },
  );

  readonly statut = computed(() => this.etat().statut);
  readonly familles = computed<Famille[]>(() => {
    const etat = this.etat();
    return etat.statut === 'pret' ? etat.catalogue.familles : [];
  });
  readonly axes = computed<string[]>(() => {
    const etat = this.etat();
    return etat.statut === 'pret' ? etat.catalogue.axes : [];
  });
  readonly misesEnPage = computed<MiseEnPage[]>(() => {
    const etat = this.etat();
    return etat.statut === 'pret' ? (etat.catalogue.mises_en_page ?? []) : [];
  });
}
