import test from 'node:test';
import assert from 'node:assert/strict';
import {optimizeRouteBatch} from '../src/route-batch.js';
const proposal=(id,gain)=>({edgeId:id,before:{score:gain+1},after:{score:1}});
test('v25.4 sélectionne des propositions compatibles',()=>{const b={proposals:[proposal('a',10),proposal('b',20),proposal('c',5)],conflicts:[{a:'a',b:'b',crossFabric:true}]};const r=optimizeRouteBatch(b);assert.deepEqual(r.selectedIds,['b','c']);assert.equal(r.estimatedGain,25);});
test('v25.4 optimise sans muter les entrées',()=>{const b={proposals:[proposal('a',3)],conflicts:[]};const before=JSON.stringify(b);optimizeRouteBatch(b);assert.equal(JSON.stringify(b),before);});
test('v25.4 résultat déterministe',()=>{const b={proposals:[proposal('z',10),proposal('a',10)],conflicts:[{a:'z',b:'a'}]};assert.deepEqual(optimizeRouteBatch(b),optimizeRouteBatch(b));});
test('v25.4 refuse paramètres invalides',()=>assert.throws(()=>optimizeRouteBatch({proposals:[],conflicts:[]},{fabricPriority:0}),/invalide/));
test('v25.4 ne sélectionne pas de gain nul',()=>assert.deepEqual(optimizeRouteBatch({proposals:[proposal('a',0)],conflicts:[]}).selectedIds,[]));
