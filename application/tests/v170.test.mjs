import test from 'node:test';
import assert from 'node:assert/strict';
import {routeSmart} from '../src/routing.js';
const a={x:0,y:0,w:60,h:50},b={x:300,y:0,w:60,h:50};
test('fast smart routing remains anchored',()=>{const r=routeSmart(a,b,[],[],{fast:true});assert.ok(r.points.length>=2);assert.ok(Number.isFinite(r.score));});
test('fast smart routing deterministic',()=>{assert.deepEqual(routeSmart(a,b,[],[],{fast:true}),routeSmart(a,b,[],[],{fast:true}));});
test('fast smart routing accepts obstacles',()=>{const r=routeSmart(a,b,[{x:140,y:-30,w:70,h:100}],[],{fast:true});assert.ok(r.points.length>=2);});
test('standard smart routing preserved',()=>{assert.ok(routeSmart(a,b).points.length>=2);});
