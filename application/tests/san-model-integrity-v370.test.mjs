import test from 'node:test';
import assert from 'node:assert/strict';
import { analyzeSanRedundancy } from '../src/san-redundancy-v363.js';
const codes = d => analyzeSanRedundancy(d).issues.map(x=>x.code);
test('duplicate node IDs are reported, never silently ignored',()=>assert.ok(codes({nodes:[{id:'a'},{id:'a'}],edges:[]}).includes('DUPLICATE_NODE_ID')));
test('missing node IDs are reported',()=>assert.ok(codes({nodes:[{type:'server'}],edges:[]}).includes('MISSING_NODE_ID')));
test('duplicate edge IDs are reported',()=>assert.ok(codes({nodes:[{id:'a'},{id:'b'}],edges:[{id:'x',source:'a',target:'b',fabric:'A'},{id:'x',source:'a',target:'b',fabric:'B'}]}).includes('DUPLICATE_EDGE_ID')));
test('self links are warned about',()=>assert.ok(codes({nodes:[{id:'a'}],edges:[{id:'x',source:'a',target:'a',fabric:'A'}]}).includes('SELF_LOOP')));
test('diagnostic remains read-only',()=>{const d={nodes:[{id:'a'}],edges:[]};const before=JSON.stringify(d);analyzeSanRedundancy(d);assert.equal(JSON.stringify(d),before)});
