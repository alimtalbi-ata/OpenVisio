import test from 'node:test';
import assert from 'node:assert/strict';
import {createEdgeMutationSession} from '../src/edge-mutation-tracker.js';
import {readFileSync} from 'node:fs';
const edge=(id,offset=0)=>({id,from:'a',to:'b',style:'orthogonal',offset});
test('renderGraph uses one persistent mutation session per canvas',()=>{const source=readFileSync(new URL('../src/renderer.js',import.meta.url),'utf8');assert.match(source,/previous\.edgeMutationSession=createEdgeMutationSession\(state\.edges\)/);assert.match(source,/reconcileEdgeTransaction\(previous\.edgeMutationSession,state\.edges,invalidateCachedEdgeRoutes\)/);});
test('mutation session detects edits and stable repeated renders',()=>{const e=edge('a');const session=createEdgeMutationSession([e]);assert.equal(session.reconcile([e]).changed,false);e.offset=7;assert.deepEqual(session.reconcile([e]).dirty,['a']);assert.equal(session.reconcile([e]).changed,false);});
test('mutation session handles delete and undo',()=>{const session=createEdgeMutationSession([edge('a')]);assert.deepEqual(session.reconcile([]).dirty,['a']);assert.deepEqual(session.reconcile([edge('a')]).dirty,['a']);});
