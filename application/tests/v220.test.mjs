import test from 'node:test';
import assert from 'node:assert/strict';
import {planParallelLanes,separateSharedSegments} from '../src/routing.js';
test('SAN lane order stable across input permutations',()=>assert.deepEqual([...planParallelLanes(['z','a','m'])],[...planParallelLanes(['m','z','a'])]));
test('SAN lane offsets symmetrical',()=>assert.deepEqual([...planParallelLanes(['a','b','c']).values()],[-10,0,10]));
test('SAN lanes deduplicate edge IDs',()=>assert.equal(planParallelLanes(['a','a','b']).size,2));
test('SAN lanes respect maximum',()=>assert.equal(planParallelLanes(['a','b','c'],{maxLanes:2}).size,2));
test('SAN lane configuration validated',()=>assert.throws(()=>planParallelLanes(['a'],{spacing:0}),/Invalid/));
test('shared segment routing deterministic despite edge ordering',()=>{const pts=[{x:0,y:0},{x:10,y:0},{x:110,y:0},{x:120,y:0}];const routes=new Map(['z','a','m'].map(id=>[id,{points:pts}]));const a=separateSharedSegments([{id:'z'},{id:'a'},{id:'m'}],routes);const b=separateSharedSegments([{id:'m'},{id:'z'},{id:'a'}],routes);assert.deepEqual([...a].sort(),[...b].sort());});
