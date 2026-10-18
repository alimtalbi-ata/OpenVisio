import test from 'node:test';
import assert from 'node:assert/strict';
import {affectedGraphElements} from '../src/renderer.js';
test('node movement dirties incident edge',()=>{const a={nodes:[{id:'n1',x:0},{id:'n2',x:10}],edges:[{id:'e1',from:'n1',to:'n2'}]};const b=structuredClone(a);b.nodes[0].x=4;const r=affectedGraphElements(a,b);assert.deepEqual([...r.edges],['e1']);assert.equal(r.geometryChanged,true)});
test('unrelated visual label does not change routing geometry',()=>{const a={nodes:[{id:'n1',x:0}],edges:[]};const b=structuredClone(a);b.nodes[0].label='new';assert.equal(affectedGraphElements(a,b).geometryChanged,false)});
