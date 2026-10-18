import test from 'node:test';
import assert from 'node:assert/strict';
import {routeIntersectsZone,spatialRoutingImpact} from '../src/spatial-routing.js';
const z={left:40,right:60,top:40,bottom:60};
test('L-shaped route does not collide with empty bounding box',()=>assert.equal(routeIntersectsZone({points:[{x:0,y:0},{x:100,y:0},{x:100,y:100}]},z),false));
test('horizontal segment intersects zone',()=>assert.equal(routeIntersectsZone({points:[{x:0,y:50},{x:100,y:50}]},z),true));
test('diagonal segment intersects zone',()=>assert.equal(routeIntersectsZone({points:[{x:0,y:0},{x:100,y:100}]},z),true));
test('parallel segment misses zone',()=>assert.equal(routeIntersectsZone({points:[{x:0,y:70},{x:100,y:70}]},z),false));
test('empty route invalidates conservatively',()=>assert.equal(routeIntersectsZone(null,z),true));
test('spatial impact avoids false-positive bounding box',()=>{
 const nodes=[{id:'a',x:0,y:0,w:10,h:10},{id:'b',x:100,y:100,w:10,h:10},{id:'c',x:45,y:45,w:10,h:10}];
 const edges=[{id:'ab',from:'a',to:'b'}];
 const moved=structuredClone(nodes);moved[2].x=46;
 const impact=spatialRoutingImpact({nodes,edges},{nodes:moved,edges},new Map([['ab',{points:[{x:0,y:0},{x:100,y:0},{x:100,y:100}]}]]),{margin:0});
 assert.equal(impact.changedEdges.has('ab'),false);
});
test('spatial impact invalidates crossing segment',()=>{
 const nodes=[{id:'a',x:0,y:0,w:10,h:10},{id:'b',x:100,y:100,w:10,h:10},{id:'c',x:45,y:45,w:10,h:10}];
 const edges=[{id:'ab',from:'a',to:'b'}];
 const moved=structuredClone(nodes);moved[2].x=46;
 const impact=spatialRoutingImpact({nodes,edges},{nodes:moved,edges},new Map([['ab',{points:[{x:0,y:50},{x:100,y:50}]}]]),{margin:0});
 assert.equal(impact.changedEdges.has('ab'),true);
});
