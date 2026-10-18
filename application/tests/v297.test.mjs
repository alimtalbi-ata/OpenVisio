import test from 'node:test';
import assert from 'node:assert/strict';
import {commonSanDependencies} from '../src/san-spof-dependencies.js';
test('composant commun A/B détecté',()=>assert.deepEqual(commonSanDependencies([{pair:'h→s',fabric:'A',nodes:['h','swA']},{pair:'h→s',fabric:'B',nodes:['h','swB']}]).map(x=>x.componentId),['h']));
test('aucun recouvrement',()=>assert.equal(commonSanDependencies([{pair:'x',fabric:'A',nodes:['a']},{pair:'x',fabric:'B',nodes:['b']}]).length,0));
test('entrées invalides ignorées',()=>assert.deepEqual(commonSanDependencies([null,{}, {pair:'x',fabric:'?',nodes:['a']}]),[]));
test('résultat déterministe sans doublons',()=>assert.deepEqual(commonSanDependencies([{pair:'x',fabric:'B',nodes:['c','c']},{pair:'x',fabric:'A',nodes:['c']}]),commonSanDependencies([{pair:'x',fabric:'A',nodes:['c']},{pair:'x',fabric:'B',nodes:['c']}])));
