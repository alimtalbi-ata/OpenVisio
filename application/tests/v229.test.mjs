import test from 'node:test';
import assert from 'node:assert/strict';
import {buildDenseTopologySummary} from '../src/dense-report.js';
import {analyzeDenseRouteBundles} from '../src/routing.js';
const route=(...p)=>({points:p.map(([x,y])=>({x,y}))});
test('dense summary exposes completeness',()=>{const d=analyzeDenseRouteBundles(new Map([['a',route([0,0],[10,0])]]));assert.match(buildDenseTopologySummary(d),/Analyse complète/)});
test('dense summary marks partial analysis',()=>{const d=analyzeDenseRouteBundles(new Map([['a',route([0,0],[10,0])],['b',route([0,0],[10,0])],['c',route([0,0],[10,0])]]),{maxPairs:1});assert.match(buildDenseTopologySummary(d),/Analyse partielle/)});
test('dense summary distinguishes limited findings',()=>{const d=analyzeDenseRouteBundles(new Map([['a',route([0,0],[10,0])],['b',route([0,0],[10,0])],['c',route([0,0],[10,0])]]),{maxFindings:1});assert.match(buildDenseTopologySummary(d),/Résultats limités/)});
test('dense summary displays pair count',()=>{const d=analyzeDenseRouteBundles(new Map([['a',route([0,0],[10,0])]]));assert.match(buildDenseTopologySummary(d),/Paires examinées : 0/)});
