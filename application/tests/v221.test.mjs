import test from 'node:test';
import assert from 'node:assert/strict';
import {separateParallelRoutes} from '../src/routing.js';
const pts=[{x:0,y:0},{x:120,y:0}];
const mk=(ids)=>({edges:ids.map(id=>({id})),routes:new Map(ids.map(id=>[id,{points:pts,path:'M 0 0 L 120 0'}]))});
test('parallel SAN lanes are stable under reordered edges',()=>{const a=mk(['z','a','m']),b=mk(['m','z','a']);const x=separateParallelRoutes(a.edges,a.routes),y=separateParallelRoutes(b.edges,b.routes);for(const id of ['z','a','m'])assert.deepEqual(x.get(id),y.get(id));});
test('parallel SAN lanes respect locked manual waypoints',()=>{const a=mk(['a','b']);a.edges[0].waypoints=[{x:60,y:20}];const r=separateParallelRoutes(a.edges,a.routes);assert.equal(r.get('a').laneOffset,undefined);});
test('parallel SAN lanes do not cross obstacles',()=>{const a=mk(['a','b']);const r=separateParallelRoutes(a.edges,a.routes,{obstacles:[{x:45,y:-20,w:30,h:40}]});assert.equal(r.get('a').laneOffset,undefined);assert.equal(r.get('b').laneOffset,undefined);});
test('parallel SAN lanes obey cap independent of input order',()=>{const a=mk(['z','c','a','b']);const r=separateParallelRoutes(a.edges,a.routes,{maxLanes:2});assert.equal(r.get('z').laneOffset,undefined);assert.equal(r.get('c').laneOffset,undefined);assert.equal(r.get('a').laneOffset,-6);assert.equal(r.get('b').laneOffset,6);});
