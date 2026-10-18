import test from 'node:test';
import assert from 'node:assert/strict';
import {qualifyLocalRouteUpdate} from '../src/spatial-routing.js';
import {lastRoutingDecision} from '../src/renderer.js';
const node=(id,x)=>({id,x,y:0,w:50,h:40});
const edge=(id,from,to)=>({id,from,to,style:'orthogonal'});
test('route guard: unknown canvas exposes safe default',()=>assert.equal(lastRoutingDecision({}).mode,'not-measured'));
test('route guard: rejects missing route',()=>{const s={nodes:[node('a',0),node('b',100)],edges:[edge('e','a','b')]};assert.equal(qualifyLocalRouteUpdate(s,s,new Map()).eligible,false)});
test('route guard: rejects global bundle dependency',()=>{const old={nodes:[node('a',0),node('b',100),node('c',200)],edges:[edge('e','a','b'),edge('f','b','c')]};const next=structuredClone(old);next.nodes[0].x=20;const routes=new Map([['e',{points:[{x:0,y:0},{x:100,y:0}]}],['f',{points:[{x:100,y:0},{x:200,y:0}]}]]);assert.equal(qualifyLocalRouteUpdate(old,next,routes).eligible,false)});
