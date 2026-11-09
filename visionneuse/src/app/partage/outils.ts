import { DOCUMENT } from '@angular/common';
import {
  afterNextRender,
  DestroyRef,
  Directive,
  effect,
  ElementRef,
  inject,
  input,
  Pipe,
  PipeTransform,
} from '@angular/core';

import { Theme } from './preferences';

/** Noms des types de blocs (src/fiche/models.py, BlockKind) tels que l'étudiant les lit. */
export const LIBELLES_BLOCS: Record<string, string> = {
  texte: 'Texte',
  definition: 'Définition',
  encadre: 'Encadré',
  tableau: 'Tableau',
  etapes: 'Étapes',
  frise: 'Frise',
  decision: 'Arbre de décision',
  exemple: 'Exemple résolu',
  piege: 'Piège',
  essentiel: "L'essentiel",
  autotest: 'Teste-toi',
};

@Pipe({ name: 'libelleBloc' })
export class LibelleBlocPipe implements PipeTransform {
  transform(type: string): string {
    return LIBELLES_BLOCS[type] ?? type;
  }
}

/** Sous-dossier d'apercus/ où vivent les fiches rendues par une mise en page. */
export const DOSSIER_MEP = 'mep/';

/**
 * Adresse d'une fiche d'aperçu : `apercus/<id>.html` pour un gabarit, `apercus/mep/<id>.html`
 * pour une mise en page. La page lit ?theme pour suivre le thème choisi.
 */
export function lienApercu(id: string, theme: Theme, recharge = 0, dossier = ''): string {
  const params = new URLSearchParams();
  if (theme !== 'auto') params.set('theme', theme);
  if (recharge) params.set('r', String(recharge));
  const requete = params.toString();
  return `apercus/${dossier}${encodeURIComponent(id)}.html${requete ? '?' + requete : ''}`;
}

@Pipe({ name: 'lienApercu' })
export class LienApercuPipe implements PipeTransform {
  transform(id: string, theme: Theme, recharge = 0, dossier = ''): string {
    return lienApercu(id, theme, recharge, dossier);
  }
}

/**
 * Charge une adresse dans un cadre sans toucher à l'historique. Changer `src` ajouterait une
 * entrée : le bouton Retour reculerait alors dans le cadre et non dans la visionneuse, et la
 * fiche affichée ne correspondrait plus au gabarit décrit.
 */
@Directive({ selector: 'iframe[appCadre]' })
export class CadreDirective {
  readonly appCadre = input.required<string>();

  constructor() {
    const cadre = inject<ElementRef<HTMLIFrameElement>>(ElementRef).nativeElement;
    const base = inject(DOCUMENT).baseURI;
    effect(() => {
      // Absolue : relative, elle serait résolue depuis la page du cadre (apercus/apercus/…).
      const url = new URL(this.appCadre(), base).href;
      const fenetre = cadre.contentWindow;
      if (!cadre.getAttribute('src') || !fenetre) {
        cadre.src = url;
        return;
      }
      try {
        fenetre.location.replace(url);
      } catch {
        cadre.src = url;
      }
    });
  }
}

/**
 * Réduit le cadre d'une vignette à la largeur de son conteneur. Le cadre est composé à la
 * largeur fixée par le CSS (860 px pour un gabarit, 1000 px pour une mise en page) ;
 * offsetWidth la donne sans tenir compte de la transformation.
 */
@Directive({ selector: '[appAjusterPage]' })
export class AjusterPageDirective {
  constructor() {
    const hote = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      const ajuster = () => {
        const cadre = hote.querySelector('iframe');
        if (cadre && cadre.offsetWidth) {
          cadre.style.transform = `scale(${hote.clientWidth / cadre.offsetWidth})`;
        }
      };
      ajuster();
      if (typeof ResizeObserver === 'undefined') return;
      const observateur = new ResizeObserver(ajuster);
      observateur.observe(hote);
      destroyRef.onDestroy(() => observateur.disconnect());
    });
  }
}
