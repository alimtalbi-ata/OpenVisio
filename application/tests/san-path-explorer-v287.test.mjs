import test from 'node:test';import assert from 'node:assert/strict';import {exploreSanPaths} from '../src/san-path-explorer.js';
const nodes=[{id:'h',type:'server'},{id:'a',type:'switch'},{id:'b',type:'switch'},{id:'s',type:'storage'}];
const edges=[{id:'1',from:'h',to:'a',fabric:'A'},{id:'2',from:'a',to:'s',fabric:'A'},{id:'3',from:'h',to:'b',fabric:'B'},{id:'4',from:'b',to:'s',fabric:'B'}];
test('two disjoint fabrics',()=>{const r=exploreSanPaths({nodes,edges});assert.equal(r.paths.length,2);assert.equal(r.resilience[0].disjointDocumented,true)});
test('missing B is flagged',()=>{const r=exploreSanPaths({nodes,edges:edges.slice(0,2)});assert.ok(r.resilience[0].issues.includes('FABRIC_AB_NOT_DEMONSTRATED'))});
test('unknown fabric is not assigned A',()=>{const r=exploreSanPaths({nodes,edges:edges.map(e=>({...e,fabric:null}))});assert.equal(r.resilience[0].fabricA,0)});
test('does not mutate inputs',()=>{const d={nodes,edges};const before=JSON.stringify(d);exploreSanPaths(d);assert.equal(JSON.stringify(d),before)});
test('cycles terminate',()=>{const r=exploreSanPaths({nodes,edges:[...edges,{id:'5',from:'a',to:'b',fabric:'A'}]});assert.ok(r.paths.length<30)});
