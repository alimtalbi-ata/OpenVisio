import test from 'node:test';
import assert from 'node:assert/strict';
import {createRouteStore,createRevisionedRouteIndex} from '../src/spatial-routing.js';
test('cache hit without mutation',()=>{const s=createRouteStore(new Map([['x',{points:[{x:0,y:0},{x:2,y:2}]}]])),c=createRevisionedRouteIndex();assert.strictEqual(s.index(c),s.index(c));assert.deepEqual(c.stats(),{builds:1,hits:1});});
test('mutation invalidates cache',()=>{const s=createRouteStore(),c=createRevisionedRouteIndex();const a=s.index(c);s.set('x',{points:[{x:1,y:1},{x:4,y:4}]});assert.notStrictEqual(s.index(c),a);assert.equal(c.stats().builds,2);});
test('snapshot map mutation cannot modify store',()=>{const s=createRouteStore();const copy=s.snapshot();copy.set('x',{});assert.equal(s.size,0);assert.equal(s.revision,0);});
test('delete absent and clear empty do not increment revision',()=>{const s=createRouteStore();assert.equal(s.delete('x'),false);assert.equal(s.clear(),false);assert.equal(s.revision,0);});
test('replace validates atomically',()=>{const s=createRouteStore();assert.throws(()=>s.replace({}));assert.equal(s.revision,0);s.replace(new Map([['x',{}]]));assert.equal(s.size,1);assert.equal(s.revision,1);});
