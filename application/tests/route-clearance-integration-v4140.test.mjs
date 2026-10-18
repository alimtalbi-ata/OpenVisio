import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {inspectRouteClearance} from '../src/route-clearance.js';
import {lastRouteClearanceDiagnostics} from '../src/renderer.js';
test('v41.40 route clearance detects intersecting obstacle',()=>{
 const result=inspectRouteClearance([{x:0,y:5},{x:30,y:5}],[{x:10,y:0,w:10,h:10}]);
 assert.equal(result.valid,false);
 assert.ok(result.issues.some(x=>x.type==='obstacle-intersection'));
});
test('v41.40 route clearance accepts unobstructed orthogonal path',()=>{
 assert.equal(inspectRouteClearance([{x:0,y:0},{x:0,y:30}],[{x:10,y:0,w:10,h:10}]).valid,true);
});
test('v41.40 diagnostic snapshots are isolated',()=>{
 const svg={};const first=lastRouteClearanceDiagnostics(svg);first.edges.push({edgeId:'fake'});
 assert.deepEqual(lastRouteClearanceDiagnostics(svg),{checked:0,invalid:0,edges:[]});
});
test('v41.40 renderer checks final routes and publishes results',()=>{
 const code=readFileSync(new URL('../src/renderer.js',import.meta.url),'utf8');
 assert.match(code,/classifyRouteClearance\(routed\.points/);
 assert.match(code,/clearanceDiagnostics\.set\(svg/);
});
