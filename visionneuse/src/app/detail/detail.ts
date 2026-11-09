import {
  afterRenderEffect,
  Component,
  computed,
  effect,
  ElementRef,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { Title } from '@angular/platform-browser';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

import { Description } from '../description/description';
import { CatalogueService } from '../partage/catalogue';
import { Famille } from '../partage/modeles';
import { CadreDirective, lienApercu, LienApercuPipe } from '../partage/outils';
import { Largeur, PreferencesService } from '../partage/preferences';
import { ThemeChoix } from '../partage/theme-choix';

/**
 * Un gabarit : la liste des gabarits, l'aperçu réel de la fiche, sa description.
 * Clavier : flèches gauche et droite pour changer de gabarit, Échap pour la galerie.
 */
@Component({
  selector: 'app-detail',
  imports: [RouterLink, RouterLinkActive, ThemeChoix, CadreDirective, LienApercuPipe, Description],
  templateUrl: './detail.html',
  styleUrl: './detail.css',
  host: { '(document:keydown)': 'clavier($event)' },
})
export class Detail {
  /** Lié au paramètre de route :id. */
  readonly id = input.required<string>();

  protected readonly catalogue = inject(CatalogueService);
  protected readonly prefs = inject(PreferencesService);
  private readonly router = inject(Router);

  protected readonly famille = computed(() =>
    this.catalogue.familles().find((f) => f.id === this.id()),
  );
  protected readonly precedente = computed(() => this.voisine(-1));
  protected readonly suivante = computed(() => this.voisine(1));
  /** Change à chaque clic sur Recharger, pour relire la fiche après une construction. */
  protected readonly recharge = signal(0);
  protected readonly lienSeul = computed(() => lienApercu(this.id(), this.prefs.theme()));
  protected readonly largeurs: { valeur: Largeur; libelle: string }[] = [
    { valeur: 'ordi', libelle: 'Ordinateur' },
    { valeur: 'telephone', libelle: 'Téléphone' },
  ];

  private readonly liste = viewChild<ElementRef<HTMLElement>>('liste');

  constructor() {
    const titre = inject(Title);
    effect(() => {
      const f = this.famille();
      if (f) titre.setTitle(`${f.nom}, gabarits de fiche`);
      // Identifiant inconnu une fois le catalogue lu : retour à la galerie.
      else if (this.catalogue.statut() === 'pret') this.router.navigate(['/']);
    });
    // Sur petit écran la liste défile en largeur : garder le gabarit ouvert en vue.
    afterRenderEffect(() => {
      this.famille();
      this.liste()
        ?.nativeElement.querySelector('[aria-current="page"]')
        ?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
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
    if (cible) this.router.navigate(['/gabarit', cible]);
    else if (e.key === 'Escape') this.router.navigate(['/']);
  }

  private voisine(pas: number): Famille | undefined {
    const familles = this.catalogue.familles();
    const i = familles.findIndex((f) => f.id === this.id());
    if (i < 0) return undefined;
    return familles[(i + pas + familles.length) % familles.length];
  }
}
