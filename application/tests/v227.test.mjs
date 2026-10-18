import test from 'node:test';import assert from 'node:assert/strict';
import {routeBounds,boundsIntersect,proposeRouteOffset} from '../src/route-preview.js';
test('bounding boxes of orthogonal paths',()=>assert.deepEqual(routeBounds([{x:9,y:3},{x:-2,y:3},{x:-2,y:15}]),{minX:-2,maxX:9,minY:3,maxY:15}));
test('invalid paths conservatively rejected',()=>assert.equal(routeBounds([{x:0,y:0},{x:NaN,y:1}]),null));
test('separated bounding boxes skip expensive intersection',()=>assert.equal(boundsIntersect({minX:0,maxX:10,minY:0,maxY:10},{minX:20,maxX:30,minY:20,maxY:30}),false));
test('touching boxes retained conservatively',()=>assert.equal(boundsIntersect({minX:0,maxX:10,minY:0,maxY:10},{minX:10,maxX:20,minY:10,maxY:20}),true));
test('padding retains close obstacles',()=>assert.equal(boundsIntersect({minX:0,maxX:10,minY:0,maxY:10},{minX:12,maxX:20,minY:0,maxY:10},4),true));
test('far away routes do not alter preview',()=>{const edge={id:'e',from:'a',to:'b',style:'orthogonal'};const nodes=[{id:'a',x:0,y:0,w:20,h:20},{id:'b',x:100,y:80,w:20,h:20}];const base=new Map([['e',{points:[{x:20,y:10},{x:60,y:10},{x:100,y:10}]}],['overlap',{points:[{x:20,y:10},{x:100,y:10}]}]]);const a=proposeRouteOffset(edge,nodes,base);base.set('far',{points:[{x:10000,y:10000},{x:20000,y:10000}]});const b=proposeRouteOffset(edge,nodes,base);assert.equal(a.status,b.status);assert.equal(a.offset,b.offset);assert.deepEqual(a.after,b.after);});
