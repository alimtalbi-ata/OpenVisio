import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {routeAvoidingObstacles} from '../src/routing.js';
const a={x:0,y:0,w:60,h:40},b={x:300,y:0,w:60,h:40};
test('invalid routing step rejected',()=>{for(const n of [0,-1,2,Infinity,NaN,201])assert.throws(()=>routeAvoidingObstacles(a,b,[],n));});
test('invalid obstacle rejected',()=>assert.throws(()=>routeAvoidingObstacles(a,b,[{x:20,y:20,w:-1,h:30}])));
test('invalid endpoint rejected',()=>assert.throws(()=>routeAvoidingObstacles({...a,w:0},b)));
test('valid obstacle avoidance remains functional',()=>{const r=routeAvoidingObstacles(a,b,[{x:150,y:-20,w:50,h:100}]);assert.ok(r.points.length>=2);assert.equal(r.avoided,true);});
test('Windows smoke validates security headers',()=>assert.match(readFileSync(new URL('../windows/Validate-OpenVisio-Windows.ps1',import.meta.url),'utf8'),/X-Frame-Options/));
test('Windows smoke checks POST rejected',()=>assert.match(readFileSync(new URL('../windows/Validate-OpenVisio-Windows.ps1',import.meta.url),'utf8'),/POST did not return 405/));
test('Windows smoke checks missing asset',()=>assert.match(readFileSync(new URL('../windows/Validate-OpenVisio-Windows.ps1',import.meta.url),'utf8'),/Missing asset did not return 404/));
