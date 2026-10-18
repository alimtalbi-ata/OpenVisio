import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const py=fs.readFileSync(new URL('./browser-san-performance.py',import.meta.url),'utf8');
test('v24.7 teste insertion native',()=>assert.match(py,/page\.locator\('\[data-shape="server"\]'\)/));
test('v24.7 vérifie mouvement natif',()=>assert.match(py,/assert before!=after/));
test('v24.7 crée connexion native',()=>assert.match(py,/native_edges\.count\(\)>=1/));
test('v24.7 vérifie les tracés',()=>assert.match(py,/paths_checked/));
test('v24.7 ne prétend pas à une capture sur échec',()=>assert.match(py,/if screenshot:/));
