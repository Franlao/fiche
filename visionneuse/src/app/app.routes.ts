import { Routes } from '@angular/router';

import { Detail } from './detail/detail';
import { DetailMep } from './detail-mep/detail-mep';
import { Galerie } from './galerie/galerie';

export const routes: Routes = [
  { path: '', component: Galerie, title: 'Gabarits de fiche' },
  { path: 'gabarit/:id', component: Detail },
  { path: 'mise-en-page/:id', component: DetailMep },
  { path: '**', redirectTo: '' },
];
