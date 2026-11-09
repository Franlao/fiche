// Les aperçus restent dans ../apercus (source de vérité, construits par apercus/build.py).
// Angular ne copie que des ressources situées dans son dossier : on y crée un lien vers eux
// (jonction sous Windows, lien symbolique ailleurs). Lancé avant npm start, build et test.
import { existsSync, lstatSync, symlinkSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const racine = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const lien = resolve(racine, 'apercus');
const cible = resolve(racine, '..', 'apercus');

if (!existsSync(resolve(cible, 'gabarits.json'))) {
  console.error(
    'apercus/gabarits.json manque : lancer « uv run python apercus/build.py » à la racine du dépôt.',
  );
  process.exit(1);
}
let present = false;
try {
  lstatSync(lien);
  present = true;
} catch {
  // Pas encore de lien.
}
if (!present) {
  symlinkSync(cible, lien, process.platform === 'win32' ? 'junction' : 'dir');
  console.log('Lien créé : visionneuse/apercus -> ../apercus');
}
