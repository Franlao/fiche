import { Component, inject } from '@angular/core';

import { PreferencesService, Theme } from './preferences';

/** Bascule Auto / Clair / Sombre, appliquée à la visionneuse et aux fiches. */
@Component({
  selector: 'app-theme-choix',
  template: `
    <div class="choix" role="group" aria-label="Thème">
      @for (option of options; track option.valeur) {
        <button
          type="button"
          [attr.aria-pressed]="prefs.theme() === option.valeur"
          (click)="prefs.theme.set(option.valeur)"
        >
          {{ option.libelle }}
        </button>
      }
    </div>
  `,
})
export class ThemeChoix {
  protected readonly prefs = inject(PreferencesService);
  protected readonly options: { valeur: Theme; libelle: string }[] = [
    { valeur: 'auto', libelle: 'Auto' },
    { valeur: 'light', libelle: 'Clair' },
    { valeur: 'dark', libelle: 'Sombre' },
  ];
}
