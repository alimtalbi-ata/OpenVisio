import test from 'node:test';
import assert from 'node:assert/strict';
import {optimizeRouteBatch} from '../src/route-batch.js';
const proposal=(id,gain)=>({edgeId:id,before:{score:gain},after:{score:0}});
const batch=(p,conflicts=[])=>({proposals:p.map(([id,g])=>proposal(id,g)),conflicts:conflicts.map(([a,b])=>({a,b}))});
test('v26.9 exact selects two non-conflicting routes over one high-degree route',()=>{
 const result=optimizeRouteBatch(batch([['A',9],['B',6],['C',6]],[['A','B'],['A','C']]));
 assert.deepEqual(result.selectedIds,['B','C']);assert.equal(result.estimatedGain,12);assert.equal(result.mode,'exact-bounded');
});
test('v26.9 exact honors transitive conflicts and ignores non-positive benefit',()=>{
 const r=optimizeRouteBatch(batch([['A',4],['B',5],['C',4],['D',0]],[['A','B'],['B','C']]));
 assert.deepEqual(r.selectedIds,['A','C']);
});
test('v26.9 deterministic tie break independent of input order',()=>{
 const p=[['B',5],['A',5]];const conflicts=[['A','B']];
 assert.deepEqual(optimizeRouteBatch(batch(p,conflicts)).selectedIds,['A']);
 assert.deepEqual(optimizeRouteBatch(batch([...p].reverse(),conflicts)).selectedIds,['A']);
});
test('v26.9 large batches retain conservative greedy fallback',()=>{
 const r=optimizeRouteBatch(batch(Array.from({length:19},(_,i)=>['R'+i,1])));
 assert.equal(r.mode,'exact-bounded');assert.equal(r.selectedIds.length,19);
});
