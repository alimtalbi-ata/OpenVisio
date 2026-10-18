import test from 'node:test';
import assert from 'node:assert/strict';
import {invalidateCachedEdgeRoute,invalidateCachedEdgeRoutes,routeCacheDiagnostics} from '../src/renderer.js';
test('v41.11: unknown connection invalidation does not mutate cache',()=>{
 const before=routeCacheDiagnostics();
 assert.equal(invalidateCachedEdgeRoute('nonexistent-v4111'),0);
 assert.deepEqual(routeCacheDiagnostics(),before);
});
test('v41.11: duplicate invalidations are idempotent',()=>{
 assert.equal(invalidateCachedEdgeRoutes(['nonexistent-v4111','nonexistent-v4111']),0);
});
test('v41.11: invalid input is rejected',()=>{
 assert.throws(()=>invalidateCachedEdgeRoutes(null),TypeError);
});
