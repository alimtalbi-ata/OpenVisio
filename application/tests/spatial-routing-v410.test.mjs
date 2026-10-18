import test from 'node:test';
import assert from 'node:assert/strict';
import {routeBounds,buildRouteSpatialIndex,queryRouteSpatialIndex,spatialRoutingImpact} from '../src/spatial-routing.js';
test('routeBounds supporte 150 000 points sans dépassement de pile',()=>{
 const points=Array.from({length:150000},(_,i)=>({x:i,y:i===0?0:-i}));
 assert.deepEqual(routeBounds({points}),{left:0,right:149999,top:-149999,bottom:0});
});
test('routeBounds refuse les coordonnées non finies',()=>{
 assert.equal(routeBounds({points:[{x:0,y:0},{x:Infinity,y:2}]}),null);
});
test('index spatial recalculé après mutation de la même Map',()=>{
 const routes=new Map([['r1',{points:[{x:0,y:0},{x:20,y:0}]}]]);
 const prev={nodes:[{id:'a',x:100,y:100,w:20,h:20}],edges:[{id:'r1',from:'x',to:'y'}]};
 const next={nodes:[{id:'a',x:110,y:110,w:20,h:20}],edges:[{id:'r1',from:'x',to:'y'}]};
 spatialRoutingImpact(prev,next,routes);
 routes.set('r1',{points:[{x:100,y:100},{x:120,y:120}]});
 const result=spatialRoutingImpact(prev,next,routes);
 assert.equal(result.changedEdges.has('r1'),true);
});
