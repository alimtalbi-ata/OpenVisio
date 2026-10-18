import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/renderer.js',import.meta.url),'utf8');
test('v41.10 rendering tracks value-based edge mutations',()=>{assert.match(src,/reconcileEdgeTransaction\(previous\.edgeMutationSession,state\.edges/);assert.match(src,/previous\.edgeMutationSession=createEdgeMutationSession/);});
test('v41.10 invalidates deleted and modified connections',()=>{assert.match(src,/reconcileEdgeTransaction\(previous\.edgeMutationSession,state\.edges/);assert.match(src,/reconcileEdgeTransaction\(previous\.edgeMutationSession,state\.edges,invalidateCachedEdgeRoutes\)/);});
