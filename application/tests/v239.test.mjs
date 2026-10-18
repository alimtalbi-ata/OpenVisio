import test from 'node:test';
import assert from 'node:assert/strict';
import {compareRoutingGeometry} from '../src/renderer.js';
import {buildRouteSpatialIndex,queryRouteSpatialIndex,routeIntersectsZone} from '../src/spatial-routing.js';
const route=(x,y)=>({points:[{x,y},{x:x+30,y},{x:x+30,y:y+20}]});
test('SAN comparison scales to 1024 independent routes',()=>{const a=new Map(Array.from({length:1024},(_,i)=>[String(i),route(i*100,0)]));assert.equal(compareRoutingGeometry(a,new Map(a)).comparedEdges,1024);});
test('SAN differential identifies exact changed route in large set',()=>{const a=new Map(Array.from({length:512},(_,i)=>[String(i),route(i*100,0)]));const b=new Map(a);b.set('255',route(25501,0));assert.deepEqual(compareRoutingGeometry(a,b).divergentEdges,['255']);});
test('spatial index candidate filtering remains conservative',()=>{const a=new Map([['near',route(0,0)],['far',route(1000,1000)]]);const zone={left:0,top:0,right:50,bottom:50};const candidates=queryRouteSpatialIndex(buildRouteSpatialIndex(a),[zone]);assert.equal(candidates.has('near'),true);assert.equal(candidates.has('far'),false);assert.equal(routeIntersectsZone(a.get('near'),zone),true);});
test('spatial index never loses an unknown invalid route',()=>{const a=new Map([['unknown',{points:[]}],['known',route(1000,1000)]]);assert.equal(queryRouteSpatialIndex(buildRouteSpatialIndex(a),[{left:0,top:0,right:50,bottom:50}]).has('unknown'),true);});
