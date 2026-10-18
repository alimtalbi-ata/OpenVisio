import test from 'node:test';import assert from 'node:assert/strict';
import {classifyEdges,clearProjection} from '../src/san-inline-simulation-v292.js';
test('classification des liens sans mutation',()=>{const r={visual:{lostEdgeIds:[1],preservedEdgeIds:[2]}};const x=classifyEdges(r);assert(x.lost.has('1'));assert(x.kept.has('2'));assert.equal(r.visual.lostEdgeIds[0],1)});
test('rapport absent est sûr',()=>{const x=classifyEdges(null);assert.equal(x.lost.size,0);assert.equal(x.kept.size,0)});
test('effacement sur racine vide',()=>{clearProjection({querySelectorAll:()=>[]})});
