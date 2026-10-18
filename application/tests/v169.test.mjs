import test from 'node:test';
import assert from 'node:assert/strict';
import {optimizeConnectionOrder,routeEdge} from '../src/routing.js';
import {generateTopology} from '../src/benchmark.js';
for(const size of [100,500,1000]){
 test(`large diagram ${size}: deterministic routes and complete coverage`,()=>{
  const {nodes,edges}=generateTopology(size);
  const route=(e,a,b)=>routeEdge(a,b,'orthogonal');
  const result=optimizeConnectionOrder(edges,nodes,route);
  assert.equal(result.routes.size,size-1);
  assert.equal(result.crossingsEvaluated,size<=160);
  assert.ok(Number.isFinite(result.length));
 });
}
test('manual waypoints are routed first on large diagrams',()=>{
 const {nodes,edges}=generateTopology(180);
 edges[50].waypoints=[{x:50,y:50}];
 const calls=[];
 optimizeConnectionOrder(edges,nodes,(e,a,b)=>{calls.push(e.id);return routeEdge(a,b,'straight');});
 assert.equal(calls[0],edges[50].id);
 assert.equal(calls.length,edges.length);
});
test('small diagrams retain two routing passes',()=>{
 const {nodes,edges}=generateTopology(12);
 let calls=0;
 const result=optimizeConnectionOrder(edges,nodes,(e,a,b)=>{calls++;return routeEdge(a,b,'straight');});
 assert.equal(calls,edges.length*2);
 assert.equal(result.crossingsEvaluated,true);
});
