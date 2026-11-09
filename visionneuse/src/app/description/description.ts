import { Component, computed, input } from '@angular/core';

import { Famille } from '../partage/modeles';
import { LIBELLES_BLOCS, LibelleBlocPipe } from '../partage/outils';

/** Ce qu'il faut savoir d'un gabarit pour juger son aperçu : intention, dosage, règles, blocs. */
@Component({
  selector: 'app-description',
  imports: [LibelleBlocPipe],
  templateUrl: './description.html',
  styleUrl: './description.css',
  host: { '[style.--fam]': 'famille().accent' },
})
export class Description {
  readonly famille = input.required<Famille>();
  readonly axes = input.required<string[]>();

  /** Blocs obligatoires en fin de chapitre, en clair : « L'essentiel, Teste-toi ». */
  protected readonly finDeChapitre = computed(() =>
    (this.famille().gabarit?.fin_de_chapitre ?? [])
      .map((type) => LIBELLES_BLOCS[type] ?? type)
      .join(', '),
  );
}
