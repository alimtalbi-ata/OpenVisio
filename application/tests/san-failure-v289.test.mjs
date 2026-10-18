import test from 'node:test';import assert from 'node:assert/strict';import {simulateSanFailure} from '../src/san-failure-simulation.js';
const doc={nodes:[{id:'h',type:'server'},{id:'a',type:'switch'},{id:'b',type:'switch'},{id:'t',type:'storage'}],edges:[{id:'1',from:'h',to:'a',fabric:'A'},{id:'2',from:'a',to:'t',fabric:'A'},{id:'3',from:'h',to:'b',fabric:'B'},{id:'4',from:'b',to:'t',fabric:'B'}]};
test('loss of fabric A leaves B route',()=>{const r=simulateSanFailure(doc,{failedFabric:'A'});assert.equal(r.affected[0].before,2);assert.equal(r.affected[0].after,1);assert.equal(r.affected[0].unreachable,false);});
test('loss of switch A leaves B route',()=>{const r=simulateSanFailure(doc,{failedNodeId:'a'});assert.equal(r.affected[0].after,1);});
test('original graph remains unchanged',()=>{const original=JSON.stringify(doc);simulateSanFailure(doc,{failedFabric:'B'});assert.equal(JSON.stringify(doc),original);});
test('invalid fabric rejected',()=>assert.throws(()=>simulateSanFailure(doc,{failedFabric:'C'}),RangeError));
