import test from 'node:test';import assert from 'node:assert/strict';
import {routeBounds} from '../src/route-preview.js';
test('v41.0 bounds sur 150000 points sans débordement de pile',()=>{const p=Array.from({length:150000},(_,i)=>({x:i,y:-i}));assert.deepEqual(routeBounds(p),{minX:0,maxX:149999,minY:-149999,maxY:-0});});
test('v41.0 géométries invalides refusées',()=>{assert.equal(routeBounds([{x:0,y:0},{x:NaN,y:1}]),null);});
