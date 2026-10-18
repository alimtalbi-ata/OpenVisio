import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('v29.1 page accessible depuis éditeur',()=>assert.match(read('index.html'),/san-impact-view.html/));
test('v29.1 simulation non destructive',()=>assert.match(read('src/san-impact-view-v291.js'),/buildSanImpactReport/));
test('v29.1 export CSV',()=>assert.match(read('src/san-impact-view-v291.js'),/sanImpactCsv/));
test('v29.1 manifeste captures explicite',()=>assert.match(read('SNAPSHOTS-V29.1.md'),/Aucune capture réelle/));
