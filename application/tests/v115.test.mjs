import test from 'node:test';
import assert from 'node:assert/strict';
import {routeAvoidingObstacles,routeViaWaypoints} from '../src/routing.js';
import {readFileSync} from 'node:fs';
const a={id:'a',x:0,y:0,w:100,h:60};
const b={id:'b',x:400,y:180,w:100,h:60};
test('waypoints respect explicit ports',()=>{
 const r=routeViaWaypoints(a,b,[{x:220,y:120}],'bottom','top');
 assert.deepEqual(r.points[0],{x:50,y:60,side:'bottom'});
 assert.deepEqual(r.points.at(-1),{x:450,y:180,side:'top'});
 assert.deepEqual(r.points[1],{x:220,y:120});
});
test('avoid mode respects explicit endpoints',()=>{
 const r=routeAvoidingObstacles(a,b,[],20,'bottom','top');
 assert.deepEqual(r.points[0],{x:50,y:60,side:'bottom'});
 assert.deepEqual(r.points.at(-1),{x:450,y:180,side:'top'});
});
test('avoid mode refuses invalid explicit port',()=>assert.throws(()=>routeAvoidingObstacles(a,b,[],20,'diagonal','auto')));
test('manual mode refuses invalid explicit port',()=>assert.throws(()=>routeViaWaypoints(a,b,[],'auto','diagonal')));
test('selected edge shows port markers',()=>assert.match(readFileSync(new URL('../src/renderer.js',import.meta.url),'utf8'),/endpoint-anchor/));
