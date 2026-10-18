import test from 'node:test';
import assert from 'node:assert/strict';
import {findPartialOverlaps,separatePartialOverlaps} from '../src/routing.js';
const edges=[{id:'a'},{id:'b'}];
const routes=()=>new Map([
 ['a',{points:[{x:0,y:0},{x:10,y:0},{x:10,y:50},{x:120,y:50},{x:120,y:100}],path:'a'}],
 ['b',{points:[{x:20,y:0},{x:30,y:0},{x:30,y:50},{x:100,y:50},{x:100,y:110}],path:'b'}]
]);
test('detects partially overlapping segments with unequal endpoints',()=>{const a=findPartialOverlaps(edges,routes());assert.equal(a.length,1);assert.equal(a[0].length,70);});
test('separates partial overlap',()=>{const r=separatePartialOverlaps(edges,routes());assert.notEqual(r.get('a').path,'a');assert.notEqual(r.get('b').path,'b');});
test('preserves first and last anchors',()=>{const r=separatePartialOverlaps(edges,routes());for(const e of edges){assert.deepEqual(r.get(e.id).points[0],routes().get(e.id).points[0]);assert.deepEqual(r.get(e.id).points.at(-1),routes().get(e.id).points.at(-1));}});
test('manual links excluded',()=>{const e=[{id:'a',waypoints:[{x:2,y:2}]},edges[1]];assert.equal(findPartialOverlaps(e,routes()).length,0);});
test('obstacle blocks detours',()=>{const r=separatePartialOverlaps(edges,routes(),{obstacles:[{x:35,y:40,w:60,h:20}]});assert.equal(r.get('a').path,'a');assert.equal(r.get('b').path,'b');});
test('different coordinates do not overlap',()=>{const r=routes();r.get('b').points[2].y=60;r.get('b').points[3].y=60;assert.equal(findPartialOverlaps(edges,r).length,0);});
test('invalid settings rejected',()=>{assert.throws(()=>findPartialOverlaps(edges,routes(),{minLength:0}));assert.throws(()=>separatePartialOverlaps(edges,routes(),{spacing:0}));});
test('deterministic routing',()=>assert.deepEqual([...separatePartialOverlaps(edges,routes())],[...separatePartialOverlaps(edges,routes())]));
