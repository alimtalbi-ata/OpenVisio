import test from 'node:test';
import assert from 'node:assert/strict';
import {separateSharedSegments} from '../src/routing.js';
const edges=[{id:'a'},{id:'b'}];
const make=()=>new Map([
 ['a',{points:[{x:0,y:0},{x:20,y:0},{x:20,y:50},{x:100,y:50},{x:100,y:80}],path:'a'}],
 ['b',{points:[{x:0,y:100},{x:20,y:100},{x:20,y:50},{x:100,y:50},{x:100,y:120}],path:'b'}]
]);
test('separates common internal segments of otherwise different routes',()=>{const r=separateSharedSegments(edges,make());assert.notEqual(r.get('a').path,'a');assert.notEqual(r.get('b').path,'b');assert.deepEqual(r.get('a').points[0],{x:0,y:0});assert.deepEqual(r.get('b').points.at(-1),{x:100,y:120});});
test('manual routes remain unchanged',()=>{const r=separateSharedSegments([{id:'a',waypoints:[{x:1,y:2}]},edges[1]],make());assert.equal(r.get('a').path,'a');});
test('single route remains unchanged',()=>{const r=separateSharedSegments([edges[0]],new Map([['a',make().get('a')]]));assert.equal(r.get('a').path,'a');});
test('invalid spacing rejected',()=>assert.throws(()=>separateSharedSegments(edges,make(),{spacing:0})));
test('obstacle blocks detour',()=>{const r=separateSharedSegments(edges,make(),{obstacles:[{x:30,y:40,w:50,h:20}]});assert.equal(r.get('a').path,'a');assert.equal(r.get('b').path,'b');});
test('results deterministic',()=>{assert.deepEqual([...separateSharedSegments(edges,make())],[...separateSharedSegments(edges,make())]);});
