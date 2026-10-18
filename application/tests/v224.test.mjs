import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {locateRouteAnomalies} from '../src/routing.js';
const route=points=>({points});
test('detect overlapping paths and link both edges',()=>{const r=new Map([['a',route([{x:0,y:0},{x:20,y:0}])],['b',route([{x:10,y:0},{x:30,y:0}])]]);assert.deepEqual(locateRouteAnomalies(r).findings,[{code:'route-overlap',edgeId:'a',otherEdgeId:'b'}]);});
test('detect crossing',()=>{const r=new Map([['a',route([{x:0,y:10},{x:20,y:10}])],['b',route([{x:10,y:0},{x:10,y:20}])]]);assert.equal(locateRouteAnomalies(r).findings[0].code,'route-crossing');});
test('invalid diagonal is flagged',()=>assert.equal(locateRouteAnomalies(new Map([['x',route([{x:0,y:0},{x:2,y:3}])]])).findings[0].code,'invalid-route'));
test('shared endpoints are not counted as crossings',()=>assert.equal(locateRouteAnomalies(new Map([['a',route([{x:0,y:0},{x:10,y:0}])],['b',route([{x:10,y:0},{x:10,y:10}])]])).findings.length,0));
test('bounded scan reports truncation',()=>assert.equal(locateRouteAnomalies(new Map([['a',route([{x:0,y:0},{x:10,y:0},{x:10,y:10}])]]),{maxSegments:1}).truncated,true));
test('UI includes navigation list',()=>{assert.match(readFileSync(new URL('../index.html',import.meta.url),'utf8'),/wiringGeometryFindings/);assert.match(readFileSync(new URL('../src/main.js',import.meta.url),'utf8'),/locateRouteAnomalies\(visibleRoutes\)/);});
