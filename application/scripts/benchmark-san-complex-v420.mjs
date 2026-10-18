import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {createRouteValueCache} from '../src/route-cache.js';
import {routeEdge} from '../src/routing.js';
const sizes=[100,500,1000], repetitions=7;
function fixture(count){
 const nodes=Array.from({length:Math.ceil(count/5)+15},(_,i)=>({id:`san-${i}`,x:(i%17)*137,y:Math.floor(i/17)*113,w:92,h:58}));
 const edges=Array.from({length:count},(_,i)=>({id:`fc-${i}`,a:i%nodes.length,b:(i*13+19)%nodes.length}));
 return {nodes,edges};
}
function trial(count,targeted){
 const {nodes,edges}=fixture(count);const cache=createRouteValueCache({limit:count+100});let computations=0;
 const keys=new Map();
 function read(e){const key=JSON.stringify([e.id,nodes[e.a],nodes[e.b]]);const old=cache.get(key);if(old!==undefined)return old;computations++;const route=routeEdge(nodes[e.a],nodes[e.b]);cache.set(key,route);keys.set(e.id,key);return route;}
 edges.forEach(read);const initial=computations;let total=0;const phases=[];let signatures=[];
 // Move, move again, undo and redo; compare route geometry at each stage.
 for(const delta of [25,-11,-14,25]){
  nodes[19].x+=delta;nodes[19].y+=Math.sign(delta)*3;
  const affected=edges.filter(e=>e.a===19||e.b===19);
  const start=performance.now();
  if(targeted){for(const e of affected){const key=keys.get(e.id);if(key!==undefined)cache.delete(key);}}else cache.clear();
  const geometry=edges.map(e=>JSON.stringify(read(e)));
  const ms=performance.now()-start;total+=ms;
  phases.push({affected:affected.length,elapsedMs:ms});signatures.push(geometry);
 }
 return {elapsedMs:total,recomputations:computations-initial,phases,signatures};
}
const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
const results=[];
for(const count of sizes){let equivalent=true;const full=[],target=[];let sample;
 for(let i=0;i<repetitions;i++){
  const a=trial(count,false),b=trial(count,true);full.push(a.elapsedMs);target.push(b.elapsedMs);
  equivalent &&= a.signatures.every((phase,j)=>phase.every((v,k)=>v===b.signatures[j][k]));
  sample={fullRecomputations:a.recomputations,targetedRecomputations:b.recomputations,affectedPerMutation:b.phases.map(p=>p.affected)};
 }
 results.push({connections:count,fullMedianMs:median(full),targetedMedianMs:median(target),geometryEquivalent:equivalent,...sample});
}
const report={version:'41.20',description:'Synthetic multi-step SAN routing benchmark; excludes SVG DOM, browser, Windows and obstacle avoidance',node:process.version,repetitions,steps:['move','move-again','undo','redo'],results};
writeFileSync(new URL('../../BENCHMARK-SAN-COMPLEX-V41.20.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));if(results.some(x=>!x.geometryEquivalent))process.exitCode=1;
