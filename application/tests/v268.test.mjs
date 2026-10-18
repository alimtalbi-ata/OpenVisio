import test from 'node:test';
import assert from 'node:assert/strict';
import {routeAvoidingObstacles, countRouteCrossings, routeSharedLength} from '../src/routing.js';
import {routeAvoidingObstacles as reference} from './routing-legacy-v265.mjs';
function rng(seed){let s=seed>>>0;return ()=>((s=(Math.imul(s,1664525)+1013904223)>>>0)/4294967296);}
const endpoint=(x,y)=>({x,y,w:40,h:40});
const cases=[];
for(let seed=1;seed<=240;seed++){
 const r=rng(seed), step=[10,16,20][seed%3];
 const from=endpoint(-20+Math.floor(r()*4)*10,-20+Math.floor(r()*4)*10);
 const to=endpoint(200+Math.floor(r()*12)*20,-40+Math.floor(r()*10)*20);
 const obstacles=Array.from({length:seed%17},()=>({x:40+Math.floor(r()*18)*20,y:-100+Math.floor(r()*15)*20,w:12+Math.floor(r()*4)*12,h:12+Math.floor(r()*4)*12}));
 cases.push({seed,from,to,obstacles,step});
}
test('v26.8 : 240 topologies deterministes, parite exacte avec le moteur de reference',()=>{
 for(const c of cases){assert.deepEqual(routeAvoidingObstacles(c.from,c.to,c.obstacles,c.step),reference(c.from,c.to,c.obstacles,c.step),`seed=${c.seed}`);}
});
test('v26.8 : reproductibilite stricte des 240 topologies',()=>{
 for(const c of cases){const first=routeAvoidingObstacles(c.from,c.to,c.obstacles,c.step);assert.deepEqual(first,routeAvoidingObstacles(c.from,c.to,c.obstacles,c.step),`seed=${c.seed}`);}
});
test('v26.8 : geometries negatives, contacts et superpositions',()=>{
 const h={points:[{x:-40,y:0},{x:60,y:0}]};
 const v={points:[{x:0,y:-40},{x:0,y:40}]};
 assert.equal(countRouteCrossings([h,v]),1);
 assert.equal(routeSharedLength(h,{points:[{x:-20,y:0},{x:0,y:0}]}),20);
});
test('v26.8 : aucune mutation des obstacles en calcul differentiel',()=>{
 for(const c of cases.slice(0,50)){const before=JSON.stringify(c);routeAvoidingObstacles(c.from,c.to,c.obstacles,c.step);assert.equal(JSON.stringify(c),before);}
});
