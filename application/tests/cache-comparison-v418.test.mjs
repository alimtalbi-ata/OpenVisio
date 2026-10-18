import test from 'node:test';import assert from 'node:assert/strict';import {createRouteValueCache} from '../src/route-cache.js';
test('targeted invalidation retains unaffected SAN routes',()=>{const c=createRouteValueCache({limit:10});for(let i=0;i<10;i++)c.set('e'+i,{points:[i]});for(let i=0;i<10;i+=2)c.delete('e'+i);assert.equal(c.stats().size,5);for(let i=1;i<10;i+=2)assert.deepEqual(c.get('e'+i),{points:[i]});});
test('full purge loses all cached routes',()=>{const c=createRouteValueCache();c.set('a',{points:[1]});c.clear();assert.equal(c.stats().size,0);});
