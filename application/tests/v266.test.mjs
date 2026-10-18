import test from 'node:test';
import assert from 'node:assert/strict';
import {routeAvoidingObstacles as optimized} from '../src/routing.js';
import {routeAvoidingObstacles as baseline} from './routing-legacy-v265.mjs';
const a={x:0,y:0,w:30,h:30},b={x:320,y:0,w:30,h:30};
function compare(obstacles,step=10){const x=optimized(a,b,obstacles,step),y=baseline(a,b,obstacles,step);assert.deepEqual(x,y);}
test('v26.6 : obstacles multiples, parité géométrique avec v26.5',()=>compare([{x:80,y:-30,w:40,h:70},{x:170,y:-20,w:40,h:60},{x:240,y:0,w:20,h:30}]));
test('v26.6 : obstacle géant, repli conservateur',()=>compare([{x:80,y:-50000,w:30,h:100000}]));
test('v26.6 : obstacles hors grille et marges',()=>compare([{x:80.5,y:-3.5,w:20.2,h:6.3},{x:120,y:40,w:30,h:30}]));
test('v26.6 : aucun obstacle',()=>compare([]));
test('v26.6 : grilles multiples',()=>{for(const step of [10,16,20])compare([{x:110,y:-40,w:45,h:80}],step)});
