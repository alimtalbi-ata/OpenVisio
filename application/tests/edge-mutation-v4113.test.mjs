import test from 'node:test';
import assert from 'node:assert/strict';
import {changedEdgeIds,createEdgeMutationSession} from '../src/edge-mutation-tracker.js';
const edge=(id,offset=0)=>({id,from:'a',to:'b',offset});
test('newly added connections are dirty',()=>{const result=changedEdgeIds(new Map([['a',JSON.stringify(['a','b',undefined,0,undefined,undefined,undefined,undefined,undefined])]]),[edge('a'),edge('b')]);assert.deepEqual(result.dirty,['b']);});
test('session detects in-place edits and supports undo redo',()=>{const a=edge('a');const session=createEdgeMutationSession([a]);a.offset=2;assert.deepEqual(session.reconcile([a]).dirty,['a']);a.offset=0;assert.deepEqual(session.reconcile([a]).dirty,['a']);assert.equal(session.reconcile([a]).changed,false);});
test('session snapshots are defensive',()=>{const session=createEdgeMutationSession([edge('a')]);const copy=session.snapshot();copy.clear();assert.equal(session.snapshot().size,1);});
test('session detects addition and deletion',()=>{const session=createEdgeMutationSession([edge('a')]);assert.deepEqual(session.reconcile([edge('a'),edge('b')]).dirty,['b']);assert.deepEqual(session.reconcile([edge('b')]).dirty,['a']);});
