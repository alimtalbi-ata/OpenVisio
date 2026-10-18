import test from 'node:test';
import assert from 'node:assert/strict';
import {buildRouteSpatialIndex,queryRouteSpatialIndex,spatialRoutingImpact} from '../src/spatial-routing.js';
const route=(x,y)=>({points:[{x,y},{x:x+20,y:y+20}]});
test('spatial grid selects local routes',()=>{const i=buildRouteSpatialIndex(new Map([['a',route(0,0)],['b',route(1000,1000)]]));assert.deepEqual([...queryRouteSpatialIndex(i,[{left:0,right:30,top:0,bottom:30}])],['a']);});
test('unknown route conservatively selected',()=>{const i=buildRouteSpatialIndex(new Map([['missing',null],['a',route(1000,1000)]]));assert.equal(queryRouteSpatialIndex(i,[{left:0,right:20,top:0,bottom:20}]).has('missing'),true);});
test('negative coordinates are indexed',()=>{const i=buildRouteSpatialIndex(new Map([['a',route(-200,-200)]]));assert.equal(queryRouteSpatialIndex(i,[{left:-210,right:-190,top:-210,bottom:-190}]).has('a'),true);});
test('invalid cell size rejected',()=>assert.throws(()=>buildRouteSpatialIndex(new Map(),{cellSize:0})));
test('spatial index preserves remote edge on move',()=>{const nodes=[{id:'a',x:0,y:0,w:10,h:10},{id:'b',x:1000,y:1000,w:10,h:10},{id:'c',x:50,y:50,w:10,h:10}];const edges=[{id:'ab',from:'a',to:'b'}];const next=structuredClone(nodes);next[2].x+=2;const routes=new Map([['ab',route(900,900)]]);assert.equal(spatialRoutingImpact({nodes,edges},{nodes:next,edges},routes,{margin:0}).changedEdges.size,0);});
