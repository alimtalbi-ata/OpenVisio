import test from 'node:test';
import assert from 'node:assert/strict';
import {qualifyLocalRouteUpdate} from '../src/spatial-routing.js';
const n=(id,x,y=0)=>({id,x,y,w:40,h:40});
const e=(id,from,to)=>({id,from,to,style:'orthogonal'});
const r=(x,y)=>({points:[{x,y},{x:x+40,y}]});
function fixture(){const old={nodes:[n('a',0),n('b',100),n('c',1000),n('d',1100)],edges:[e('ab','a','b'),e('cd','c','d')]};const next=structuredClone(old);next.nodes[0].x=10;return {old,next,routes:new Map([['ab',r(20,20)],['cd',r(1020,20)]])};}
test('independent SAN cable allows local candidate',()=>{const f=fixture();const q=qualifyLocalRouteUpdate(f.old,f.next,f.routes);assert.equal(q.eligible,true);assert.deepEqual(q.changedEdges,['ab']);});
test('shared endpoint blocks local routing',()=>{const f=fixture();f.old.edges[1].from='a';f.next.edges[1].from='a';assert.equal(qualifyLocalRouteUpdate(f.old,f.next,f.routes).eligible,false);});
test('route crossing impact zone blocks local routing',()=>{const f=fixture();f.routes.set('cd',r(10,20));assert.equal(qualifyLocalRouteUpdate(f.old,f.next,f.routes).eligible,false);});
test('missing independent route blocks local routing',()=>{const f=fixture();f.routes.delete('cd');assert.equal(qualifyLocalRouteUpdate(f.old,f.next,f.routes).eligible,false);});
test('multi-node motion blocks local routing',()=>{const f=fixture();f.next.nodes[2].x+=10;assert.equal(qualifyLocalRouteUpdate(f.old,f.next,f.routes).eligible,false);});
