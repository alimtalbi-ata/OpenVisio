import test from 'node:test';
import assert from 'node:assert/strict';
import {countRouteCrossings} from '../src/routing.js';

// Differential invariant: changing one route must not change crossings between other routes.
const route=(points)=>({points,orthogonalFanOut:true});
const random=(seed)=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
function fixture(seed,count){
 const rnd=random(seed), routes=[];
 for(let i=0;i<count;i++){
  const x=Math.floor(rnd()*600),y=Math.floor(rnd()*400);
  const dx=20+Math.floor(rnd()*150),dy=20+Math.floor(rnd()*120);
  routes.push(route([{x,y},{x:x+dx,y},{x:x+dx,y:y+dy}]));
 }
 return routes;
}
for(const count of [8,24,64]){
 test(`v41.37 differential crossing deltas, ${count} obstacle-like orthogonal routes`,()=>{
  for(let seed=1;seed<=8;seed++){
   const original=fixture(seed,count), index=seed%count;
   const changed=structuredClone(original);
   changed[index].points=changed[index].points.map(p=>({x:p.x+13,y:p.y-17}));
   const globalDelta=countRouteCrossings(changed)-countRouteCrossings(original);
   const others=original.filter((_,i)=>i!==index);
   const localDelta=countRouteCrossings([changed[index],...others])-countRouteCrossings([original[index],...others]);
   assert.equal(globalDelta,localDelta,`seed=${seed}`);
  }
 });
}
test('v41.37 undo redo restores crossing score exactly',()=>{
 const initial=fixture(941,48), moved=structuredClone(initial);
 moved[0].points=moved[0].points.map(p=>({x:p.x+55,y:p.y+20}));
 const before=countRouteCrossings(initial);
 assert.equal(countRouteCrossings(structuredClone(initial)),before);
 assert.equal(countRouteCrossings(moved),countRouteCrossings(structuredClone(moved)));
 assert.equal(countRouteCrossings(initial),before);
});
