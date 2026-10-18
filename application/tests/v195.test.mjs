import test from 'node:test';
import assert from 'node:assert/strict';
import {moveSelectionRigid} from '../src/graph-operations.js';
test('déplacement multiple conserve exactement les écarts',()=>{const a=moveSelectionRigid([{id:'a',x:5,y:15},{id:'b',x:105,y:65}],-30,-40);assert.deepEqual(a.get('a'),{x:0,y:0});assert.deepEqual(a.get('b'),{x:100,y:50});});
test('déplacement multiple positif',()=>{const a=moveSelectionRigid([{id:'a',x:5,y:15},{id:'b',x:105,y:65}],20,30);assert.deepEqual(a.get('b'),{x:125,y:95});});
test('alignement grille commun à la sélection',()=>{const a=moveSelectionRigid([{id:'a',x:3,y:7},{id:'b',x:103,y:57}],14,16,{grid:10});assert.deepEqual(a.get('a'),{x:13,y:27});assert.deepEqual(a.get('b'),{x:113,y:77});});
test('aucune mutation des coordonnées initiales',()=>{const positions=[{id:'a',x:1,y:2}];moveSelectionRigid(positions,4,5);assert.deepEqual(positions,[{id:'a',x:1,y:2}]);});
test('rejet des déplacements non finis',()=>{assert.equal(moveSelectionRigid([{id:'a',x:1,y:2}],Infinity,0).size,0);});
test('sélection vide sans erreur',()=>{assert.equal(moveSelectionRigid([],5,5).size,0);});
