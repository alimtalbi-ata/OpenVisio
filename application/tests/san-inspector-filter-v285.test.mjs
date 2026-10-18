import test from 'node:test';import assert from 'node:assert/strict';import {filterSanLines} from '../src/san-inspector-filter.js';
test('filtre A/B et informations communes',()=>{const lines=['Fabric A : lien 1','Fabric B : lien 2','WWPN : 10:00'];assert.deepEqual(filterSanLines(lines,'A'),[lines[0]]);assert.deepEqual(filterSanLines(lines,'B'),[lines[1]]);});
test('filtre inconnu',()=>assert.deepEqual(filterSanLines(['Fabric inconnue','Fabric A : lien'],'unknown'),['Fabric inconnue']));
test('entrée invalide',()=>{assert.deepEqual(filterSanLines(null),[]);assert.throws(()=>filterSanLines([],'X'),RangeError);});
