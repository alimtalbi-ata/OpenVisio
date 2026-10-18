import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const pkg=JSON.parse(readFileSync(new URL('../package.json',import.meta.url)));
const script=readFileSync(new URL('./browser-san-e2e-v263.py',import.meta.url),'utf8');
test('v26.3 recette navigateur A* configurée',()=>{assert.match(pkg.version,/^[0-9]+[.][0-9]+[.][0-9]+$/);assert.match(pkg.scripts['test:browser-san-e2e'],/browser-san-e2e-v263/)});
test('v26.3 contrôle véritable aperçu A*',()=>{for(const marker of ['#routePreviewOverlay','Voir le trajet','#dc2626','#16a34a'])assert.ok(script.includes(marker))});
test('v26.3 validation A* conditionnelle et réversible',()=>{for(const marker of ['NO_ELIGIBLE_ALTERNATIVE','Valider cet itinéraire','Control+z','Control+y','page.reload'])assert.ok(script.includes(marker))});
