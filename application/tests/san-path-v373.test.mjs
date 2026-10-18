import test from 'node:test';
import assert from 'node:assert/strict';
import {analyzeSanRedundancy} from '../src/san-redundancy-v363.js';
const nodes=[{id:'host',type:'server',multipath:true},{id:'a',type:'san-switch',zoneset:'z',zoning:['x']},{id:'b',type:'san-switch',zoneset:'z',zoning:['x']},{id:'array',type:'storage'}];
const edges=[{id:'e1',source:'host',target:'a',fabric:'A'},{id:'e2',source:'a',target:'array',fabric:'A'},{id:'e3',source:'host',target:'b',fabric:'B'},{id:'e4',source:'b',target:'array',fabric:'B'}];
test('traces both SAN fabrics with all intermediate nodes and edges',()=>{const p=analyzeSanRedundancy({nodes,edges}).paths[0];assert.deepEqual(p.routeA,{nodeIds:['host','a','array'],edgeIds:['e1','e2']});assert.deepEqual(p.routeB,{nodeIds:['host','b','array'],edgeIds:['e3','e4']});});
test('missing fabric has null trace',()=>{const p=analyzeSanRedundancy({nodes,edges:edges.slice(0,2)}).paths[0];assert.equal(p.routeB,null);assert.equal(p.fabricB,false);});
test('cyclic graph does not loop',()=>{const p=analyzeSanRedundancy({nodes,edges:[...edges,{id:'e5',source:'a',target:'host',fabric:'A'}]}).paths[0];assert.equal(p.routeA.edgeIds.length,2);});
