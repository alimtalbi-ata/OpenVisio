import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const pkg=JSON.parse(readFileSync(new URL('../package.json',import.meta.url)));
const script=readFileSync(new URL('./browser-san-e2e-v262.py',import.meta.url),'utf8');
test('v26.2 version et commande navigateur E2E',()=>{assert.ok(Number(pkg.version.split('.')[0])>=26);assert.match(pkg.scripts['test:browser-san-e2e'],/browser-san-e2e-v26[23]/)});
test('v26.2 vraie interface, pas de faux rendu',()=>{for(const id of ['#wiringBtn','#portableExportBtn','#portableImportFile','#edgesLayer'])assert.ok(script.includes(id));assert.match(script,/page\.screenshot/)});
test('v26.2 contrôle clavier et persistance',()=>{for(const term of ['Control+z','Control+y','page.reload','backup['])assert.ok(script.includes(term))});
