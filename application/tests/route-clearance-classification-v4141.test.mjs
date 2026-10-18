import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyRouteClearance} from '../src/route-clearance.js';
const obstacle=[{x:10,y:10,w:20,h:20}];
test('port lead issues are review only',()=>{const r=classifyRouteClearance([{x:0,y:20},{x:40,y:20},{x:40,y:50}],obstacle,{physicalStart:true});assert.equal(r.errors,0);assert.equal(r.reviews,1);assert.equal(r.valid,true);assert.equal(r.strictValid,false)});
test('core obstacle collision remains error',()=>{const r=classifyRouteClearance([{x:0,y:0},{x:0,y:20},{x:40,y:20}],obstacle,{physicalStart:true});assert.equal(r.errors,1);assert.equal(r.valid,false)});
test('no port flags retains strict severity',()=>{const r=classifyRouteClearance([{x:0,y:20},{x:40,y:20}],obstacle);assert.equal(r.errors,1);assert.equal(r.reviews,0)});
test('input points are not mutated',()=>{const pts=[{x:0,y:20},{x:40,y:20}];const before=JSON.stringify(pts);classifyRouteClearance(pts,obstacle,{physicalEnd:true});assert.equal(JSON.stringify(pts),before)});
