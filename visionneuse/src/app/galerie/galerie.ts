import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { CatalogueService } from '../partage/catalogue';
import {
  AjusterPageDirective,
  CadreDirective,
  DOSSIER_MEP,
  LienApercuPipe,
} from '../partage/outils';
import { PreferencesService } from '../partage/preferences';
import { ThemeChoix } from '../partage/theme-choix';

/** Toutes les fiches en vignettes A4, puis les mises en page sur un même contenu. */
@Component({
  selector: 'app-galerie',
  imports: [RouterLink, ThemeChoix, AjusterPageDirective, CadreDirective, LienApercuPipe],
  templateUrl: './galerie.html',
  styleUrl: './galerie.css',
})
export class Galerie {
  protected readonly catalogue = inject(CatalogueService);
  protected readonly prefs = inject(PreferencesService);
  protected readonly dossierMep = DOSSIER_MEP;
}
