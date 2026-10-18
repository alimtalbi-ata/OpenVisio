import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {analyzeSanRedundancy} from '../src/san-redundancy-v363.js';
const fixture=()=>JSON.parse(readFileSync(new URL('./fixtures/san-dual-fabric-v362.json',import.meta.url),'utf8'));
test('v36.3 healthy dual-fabric SAN has two independent paths',()=>{
 const result=analyzeSanRedundancy(fixture());
 assert.equal(result.ok,true);assert.equal(result.paths.length,1);assert.equal(result.paths[0].fabricA,true);assert.equal(result.paths[0].fabricB,true);assert.equal(result.paths[0].routeA.edgeIds.length,2);assert.equal(result.paths[0].routeB.edgeIds.length,2);assert.deepEqual(result.issues,[]);
});
test('v36.3 missing B fabric edge detects redundancy loss',()=>{
 const d=fixture();d.edges=d.edges.filter(e=>e.id!=='a4');
 const r=analyzeSanRedundancy(d);assert.equal(r.ok,false);assert.deepEqual(r.issues.find(i=>i.code==='REDUNDANCY_LOST').missingFabrics,['B']);
});
test('v36.3 cross fabric link is rejected',()=>{
 const d=fixture();d.edges[0].fabric='B';
 const r=analyzeSanRedundancy(d);assert.equal(r.ok,false);assert.ok(r.issues.some(i=>i.code==='FABRIC_MISMATCH'));
});
test('v36.3 missing endpoint and zoning report distinct issues',()=>{
 const d=fixture();d.edges.push({id:'bad',source:'missing',target:'array',fabric:'A'});d.nodes[1].zoning=[];
 const r=analyzeSanRedundancy(d);assert.ok(r.issues.some(i=>i.code==='DANGLING_LINK'));assert.ok(r.issues.some(i=>i.code==='ZONING_INCOMPLETE'));
});
test('v36.3 diagnostics do not mutate diagram',()=>{
 const d=fixture(), before=JSON.stringify(d);analyzeSanRedundancy(d);assert.equal(JSON.stringify(d),before);
});
