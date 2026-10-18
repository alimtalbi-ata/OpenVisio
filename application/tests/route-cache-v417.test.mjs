import test from 'node:test';
import assert from 'node:assert/strict';
import {createRouteValueCache} from '../src/route-cache.js';
test('value isolation on insertion and reading',()=>{const c=createRouteValueCache(),r={points:[{x:1,y:2}]};c.set('a',r);r.points[0].x=10;const got=c.get('a');got.points[0].x=99;assert.equal(c.get('a').points[0].x,1);});
test('LRU evicts oldest not most recently used',()=>{const c=createRouteValueCache({limit:2});c.set('a',1);c.set('b',2);assert.equal(c.get('a'),1);c.set('c',3);assert.equal(c.get('b'),undefined);assert.equal(c.get('a'),1);assert.equal(c.stats().evictions,1);});
test('failed clone leaves prior value intact',()=>{const c=createRouteValueCache();c.set('a',{ok:true});assert.throws(()=>c.set('a',{fn:()=>{}}));assert.deepEqual(c.get('a'),{ok:true});});
test('invalid limits and keys rejected',()=>{assert.throws(()=>createRouteValueCache({limit:0}));const c=createRouteValueCache();assert.throws(()=>c.set('',{}));assert.throws(()=>c.get(3));});
test('cache bounded under churn',()=>{const c=createRouteValueCache({limit:20});for(let i=0;i<1000;i++)c.set(String(i),{points:[{x:i,y:i}]});assert.equal(c.stats().size,20);assert.equal(c.stats().evictions,980);});
