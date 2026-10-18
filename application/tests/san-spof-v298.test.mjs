import test from 'node:test';import assert from 'node:assert/strict';import {analyzeSharedTransit} from '../src/san-spof-v298.js';
const nodes=[{id:'h',type:'server'},{id:'s',type:'storage'},{id:'x',type:'switch'}];
test('empty document',()=>assert.deepEqual(analyzeSharedTransit({nodes:[],edges:[]}).findings,[]));
test('terminals excluded',()=>{const d={nodes,edges:[{id:'a',from:'h',to:'s',fabric:'A'},{id:'b',from:'h',to:'s',fabric:'B'}]};assert.equal(analyzeSharedTransit(d).findings.length,0)});
test('shared transit is reported',()=>{const d={nodes,edges:[{id:'a',from:'h',to:'x',fabric:'A'},{id:'b',from:'x',to:'s',fabric:'A'},{id:'c',from:'h',to:'x',fabric:'B'},{id:'d',from:'x',to:'s',fabric:'B'}]};assert.equal(analyzeSharedTransit(d).findings[0].componentId,'x')});
