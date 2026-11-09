import { DOCUMENT } from '@angular/common';
import { effect, inject, Injectable, signal } from '@angular/core';

export type Theme = 'auto' | 'light' | 'dark';
export type Largeur = 'ordi' | 'telephone';

const THEMES: readonly Theme[] = ['auto', 'light', 'dark'];
const LARGEURS: readonly Largeur[] = ['ordi', 'telephone'];

/** Lit une préférence ; sans stockage (navigation privée, données bloquées), garde le défaut. */
function lire<T extends string>(cle: string, permis: readonly T[], defaut: T): T {
  try {
    const valeur = localStorage.getItem('visionneuse.' + cle);
    return permis.includes(valeur as T) ? (valeur as T) : defaut;
  } catch {
    return defaut;
  }
}

function ecrire(cle: string, valeur: string): void {
  try {
    localStorage.setItem('visionneuse.' + cle, valeur);
  } catch {
    // Préférence perdue au rechargement, sans gêne.
  }
}

/** Thème et largeur d'aperçu choisis par la personne qui regarde, gardés d'une visite à l'autre. */
@Injectable({ providedIn: 'root' })
export class PreferencesService {
  readonly theme = signal<Theme>(lire('theme', THEMES, 'auto'));
  readonly largeur = signal<Largeur>(lire('largeur', LARGEURS, 'ordi'));

  constructor() {
    const racine = inject(DOCUMENT).documentElement;
    effect(() => {
      const theme = this.theme();
      ecrire('theme', theme);
      if (theme === 'auto') racine.removeAttribute('data-theme');
      else racine.dataset['theme'] = theme;
    });
    effect(() => ecrire('largeur', this.largeur()));
  }
}
