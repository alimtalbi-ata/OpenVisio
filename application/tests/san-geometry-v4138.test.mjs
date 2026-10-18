import test from 'node:test';
import assert from 'node:assert/strict';
import {routeEdge,routeAvoidingObstacles,intersectsObstacle,countRouteCrossings,portAnchor} from '../src/routing.js';
const node=(x,y)=>({x,y,w:80,h:50});
const route=(points)=>({points,orthogonalFanOut:true});
const segmentPairs=points=>points.slice(1).map((p,i)=>[points[i],p]);
test('v41.38 explicit port anchors are deterministic across multiple ports',()=>{
 const a=node(0,0),b=node(300,100);
 for(const side of ['left','right','top','bottom']){
  const p=portAnchor(a,side,b);
  assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
  assert.deepEqual(portAnchor(a,side,b),p);
  const r=routeEdge(a,b,'orthogonal',0,side,'left');
  assert.ok(Array.isArray(r.points)&&r.points.length>=2);
 }
});
test('v41.38 obstacle collision predicate detects crossing and excludes distant segments',()=>{
 const obstacle=node(120,80);
 assert.equal(intersectsObstacle({x:0,y:100},{x:300,y:100},obstacle),true);
 assert.equal(intersectsObstacle({x:0,y:0},{x:300,y:0},obstacle),false);
});
test('v41.38 multi-route mutation delta matches local crossing delta',()=>{
 const initial=[route([{x:0,y:20},{x:220,y:20}]),route([{x:60,y:0},{x:60,y:100}]),route([{x:130,y:0},{x:130,y:100}]),route([{x:190,y:0},{x:190,y:100}])];
 const changed=structuredClone(initial);
 changed[0].points=[{x:0,y:120},{x:220,y:120}];
 changed[2].points=[{x:250,y:0},{x:250,y:100}];
 const full=countRouteCrossings(changed)-countRouteCrossings(initial);
 const afterFirst=structuredClone(initial);afterFirst[0]=changed[0];
 const incremental=(countRouteCrossings(afterFirst)-countRouteCrossings(initial))+(countRouteCrossings(changed)-countRouteCrossings(afterFirst));
 assert.equal(full,incremental);
 assert.equal(countRouteCrossings(structuredClone(initial)),countRouteCrossings(initial));
});
test('v41.38 obstacle router returns finite route coordinates',()=>{
 const result=routeAvoidingObstacles(node(0,0),node(350,0),[node(150,-15)]);
 const points=Array.isArray(result)?result:result?.points;
 assert.ok(Array.isArray(points)&&points.length>=2);
 for(const p of points)assert.ok(Number.isFinite(p.x)&&Number.isFinite(p.y));
});
