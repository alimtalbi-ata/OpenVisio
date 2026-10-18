import test from 'node:test';
import assert from 'node:assert/strict';
import {createRouteValueCache} from '../src/route-cache.js';
test('targeted invalidation retains other routes',()=>{const c=createRouteValueCache({limit:2});c.set('a',{p:1});c.set('b',{p:2});assert.equal(c.delete('a'),true);assert.equal(c.delete('a'),false);assert.deepEqual(c.get('b'),{p:2});assert.equal(c.get('a'),undefined);});
test('cache hit ratio reports actual reads',()=>{const c=createRouteValueCache();assert.equal(c.stats().hitRate,0);c.set('a',1);c.get('a');c.get('missing');assert.equal(c.stats().hitRate,0.5);});
test('delete rejects invalid key without mutation',()=>{const c=createRouteValueCache();c.set('a',1);assert.throws(()=>c.delete(3),TypeError);assert.equal(c.stats().size,1);});
