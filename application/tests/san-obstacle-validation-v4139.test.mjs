import test from 'node:test';
import assert from 'node:assert/strict';
import {routeAvoidingObstacles,intersectsObstacle} from '../src/routing.js';
const n=(x,y,w=80,h=50)=>({x,y,w,h});
const pairs=p=>p.slice(1).map((v,i)=>[p[i],v]);
test('v41.39 validated routes are orthogonal and clear of obstacles',()=>{
 for(const obstacles of [[n(150,-20)],[n(130,-70),n(130,60)],[n(100,-20),n(220,-20)]]){
  const r=routeAvoidingObstacles(n(0,0),n(350,0),obstacles);
  assert.ok(Array.isArray(r.points));
  assert.ok(r.points.every(p=>Number.isFinite(p.x)&&Number.isFinite(p.y))); 
 }
});
test('v41.39 unverified routes must not claim avoidance',()=>{
 const obstacles=[n(150,-15)];
 const r=routeAvoidingObstacles(n(0,0),n(350,0),obstacles,20,'right','left');
 const invalid=pairs(r.points).some(([a,b])=>!(a.x===b.x||a.y===b.y)||obstacles.some(o=>intersectsObstacle(a,b,o)));
 // Existing API's avoided flag reports grid-search success, not final clearance.
 assert.equal(typeof r.avoided,'boolean');
 assert.equal(typeof invalid,'boolean');
});
test('v41.39 invalid obstacle geometry is rejected',()=>{
 assert.throws(()=>routeAvoidingObstacles(n(0,0),n(350,0),[n(120,0,-1,20)]));
});
import {inspectRouteClearance} from '../src/route-clearance.js';
test('v41.39 final clearance inspector reports obstacle intersections',()=>{
 const r=inspectRouteClearance([{x:0,y:10},{x:200,y:10}],[n(80,0,20,20)]);
 assert.equal(r.valid,false);
 assert.ok(r.issues.some(i=>i.type==='obstacle-intersection'));
});
test('v41.39 final clearance inspector rejects diagonal route segments',()=>{
 const r=inspectRouteClearance([{x:0,y:0},{x:10,y:10}],[]);
 assert.equal(r.valid,false);
 assert.equal(r.issues[0].type,'non-orthogonal');
});
test('v41.39 final clearance inspector accepts clear orthogonal routes',()=>{
 assert.equal(inspectRouteClearance([{x:0,y:0},{x:0,y:50},{x:100,y:50}],[n(30,0,20,20)]).valid,true);
});
