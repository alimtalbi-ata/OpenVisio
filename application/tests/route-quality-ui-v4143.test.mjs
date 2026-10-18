import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
test('panneau de qualité accessible dans éditeur',()=>{assert.match(html,/id="routeQualityToggle"/);assert.match(html,/id="routeQualityResults"/);assert.match(main,/refreshRouteQualityPanel\(\)/);});
test('sélection de route contrôlée avant localisation',()=>{assert.match(main,/state\.edges\.some\(edge=>String\(edge\.id\)/);assert.match(main,/edgeViewportTarget\(/);});
