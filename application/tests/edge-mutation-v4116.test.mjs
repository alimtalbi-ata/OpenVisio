import test from 'node:test';
import assert from 'node:assert/strict';
import {createEdgeMutationSession,reconcileEdgeTransaction} from '../src/edge-mutation-tracker.js';
const e=(id,offset=0)=>({id,from:'switchA',to:'switchB',offset,fromPort:'fc1',toPort:'fc2'});
test('v41.16 port change invalidates only affected edge',()=>{const s=createEdgeMutationSession([e('a'),e('b')]);let ids=[];const changed=[{...e('a'),fromPort:'fc3'},e('b')];reconcileEdgeTransaction(s,changed,x=>ids.push(...x));assert.deepEqual(ids,['a']);});
test('v41.16 deletion and restoration both invalidate',()=>{const s=createEdgeMutationSession([e('a')]);let calls=[];reconcileEdgeTransaction(s,[],x=>calls.push(x));reconcileEdgeTransaction(s,[e('a')],x=>calls.push(x));assert.deepEqual(calls,[['a'],['a']]);});
test('v41.16 callback is skipped on stable rerender',()=>{const s=createEdgeMutationSession([e('a')]);let count=0;reconcileEdgeTransaction(s,[e('a')],()=>count++);assert.equal(count,0);});
