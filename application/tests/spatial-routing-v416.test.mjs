import test from 'node:test';
import assert from 'node:assert/strict';
import {createRouteStore,createRevisionedRouteIndex} from '../src/spatial-routing.js';
const route=()=>({points:[{x:1,y:2},{x:3,y:4}],metadata:{tags:['SAN']}});
test('initial routes do not retain external mutable references',()=>{const r=route(),s=createRouteStore(new Map([['e',r]]));r.points[0].x=99;r.metadata.tags.push('bad');assert.equal(s.get('e').points[0].x,1);assert.deepEqual(s.get('e').metadata.tags,['SAN']);});
test('set route cannot be mutated after insertion',()=>{const s=createRouteStore(),r=route();s.set('e',r);r.points[0].x=88;assert.equal(s.get('e').points[0].x,1);});
test('get and snapshot return deep independent values',()=>{const s=createRouteStore(new Map([['e',route()]]));const a=s.get('e'),b=s.snapshot();a.points[0].x=42;b.get('e').metadata.tags.push('bad');assert.equal(s.get('e').points[0].x,1);assert.deepEqual(s.get('e').metadata.tags,['SAN']);});
test('replace is atomic if a route cannot be cloned',()=>{const s=createRouteStore(new Map([['e',route()]])),rev=s.revision;assert.throws(()=>s.replace(new Map([['ok',route()],['bad',{fn:()=>0}]])));assert.equal(s.revision,rev);assert.equal(s.size,1);assert.equal(s.get('e').points[0].x,1);});
test('cache remains valid despite attempted mutation of returned route',()=>{const s=createRouteStore(new Map([['e',route()]])),c=createRevisionedRouteIndex();const first=s.index(c);s.get('e').points[0].x=999;assert.strictEqual(s.index(c),first);assert.deepEqual(c.stats(),{builds:1,hits:1});});
