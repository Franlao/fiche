import { Component, computed, effect, inject, input, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

import { CatalogueService } from '../partage/catalogue';
import { MiseEnPage } from '../partage/modeles';
import { CadreDirective, DOSSIER_MEP, lienApercu, LienApercuPipe } from '../partage/outils';
import { Largeur, PreferencesService } from '../partage/preferences';
import { ThemeChoix } from '../partage/theme-choix';

/**
 * Une mise en page : la liste des mises en page, la fiche rendue, ce qui la caractérise.
 * Même disposition et mêmes raccourcis que la vue d'un gabarit (flèches, Échap).
 */
@Component({
  selector: 'app-detail-mep',
  imports: [RouterLink, RouterLinkActive, ThemeChoix, CadreDirective, LienApercuPipe],
  templateUrl: './detail-mep.html',
  styleUrl: '../detail/detail.css',
  host: { '(document:keydown)': 'clavier($event)' },
})
export class DetailMep {
  /** Lié au paramètre de route :id. */
  readonly id = input.required<string>();

  protected readonly catalogue = inject(CatalogueService);
  protected readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  protected readonly dossierMep = DOSSIER_MEP;
  protected readonly mise = computed(() =>
    this.catalogue.misesEnPage().find((m) => m.id === this.id()),
  );
  protected readonly contenu = computed(() =>
    this.catalogue.familles().find((f) => f.id === this.mise()?.contenu),
  );
  protected readonly precedente = computed(() => this.voisine(-1));
  protected readonly suivante = computed(() => this.voisine(1));
  protected readonly recharge = signal(0);
  protected readonly lienSeul = computed(() =>
    lienApercu(this.id(), this.prefs.theme(), 0, DOSSIER_MEP),
  );
  protected readonly largeurs: { valeur: Largeur; libelle: string }[] = [
    { valeur: 'ordi', libelle: 'Ordinateur' },
    { valeur: 'telephone', libelle: 'Téléphone' },
  ];

  constructor() {
    const titre = inject(Title);
    effect(() => {
      const m = this.mise();
      if (m) titre.setTitle(`Mise en page ${m.nom}, gabarits de fiche`);
      else if (this.catalogue.statut() === 'pret') this.router.navigate(['/']);
    });
  }

  protected recharger(): void {
    this.recharge.update((n) => n + 1);
  }

  protected clavier(e: KeyboardEvent): void {
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if ((e.target as HTMLElement | null)?.closest?.('input, textarea, select')) return;
    const cible =
      e.key === 'ArrowLeft'
        ? this.precedente()?.id
        : e.key === 'ArrowRight'
          ? this.suivante()?.id
          : undefined;
    if (cible) this.router.navigate(['/mise-en-page', cible]);
    else if (e.key === 'Escape') this.router.navigate(['/']);
  }

  private voisine(pas: number): MiseEnPage | undefined {
    const mises = this.catalogue.misesEnPage();
    const i = mises.findIndex((m) => m.id === this.id());
    if (i < 0) return undefined;
    return mises[(i + pas + mises.length) % mises.length];
  }
}
