import test from 'node:test';
import assert from 'node:assert/strict';
import {createRouteValueCache} from '../src/route-cache.js';
import {invalidateCachedEdgeRoute,invalidateCachedEdgeRoutes,routeCacheDiagnostics} from '../src/renderer.js';
test('eviction callback keeps index lifecycle observable',()=>{const removed=[];const c=createRouteValueCache({limit:2,onEvict:k=>removed.push(k)});c.set('a',1);c.set('b',2);c.set('c',3);assert.deepEqual(removed,['a']);c.delete('b');assert.deepEqual(removed,['a','b']);c.clear();assert.deepEqual(removed,['a','b','c']);});
test('targeted invalidation of unknown edge is safe',()=>{assert.equal(invalidateCachedEdgeRoute('unknown'),0);assert.equal(invalidateCachedEdgeRoutes(['unknown','unknown']),0);assert.ok(routeCacheDiagnostics().limit>0);});
test('invalid bulk invalidation is rejected',()=>assert.throws(()=>invalidateCachedEdgeRoutes(null),TypeError));
