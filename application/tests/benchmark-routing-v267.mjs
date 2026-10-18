import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {routeAvoidingObstacles as optimized,countRouteCrossings,routeSharedLength,routeWithFewerCrossings} from '../src/routing.js';
import {routeAvoidingObstacles as baseline} from './routing-legacy-v265.mjs';
const from={x:0,y:0,w:40,h:40},to={x:700,y:0,w:40,h:40};
const fixtures=[
 {name:'sparse',obstacles:[{x:220,y:-30,w:45,h:110}]},
 {name:'multiwall',obstacles:Array.from({length:12},(_,i)=>({x:85+i*45,y:i%2?-70:-20,w:22,h:85}))},
 {name:'dense',obstacles:Array.from({length:72},(_,i)=>({x:65+(i%18)*35,y:-145+Math.floor(i/18)*70,w:18,h:35}))}
];
const rounds=25;
function measure(fn,obstacles){for(let i=0;i<5;i++)fn(from,to,obstacles,10);const samples=[];let result;for(let i=0;i<rounds;i++){const t=performance.now();result=fn(from,to,obstacles,10);samples.push(performance.now()-t);}samples.sort((a,b)=>a-b);return {medianMs:samples[Math.floor(rounds/2)],p95Ms:samples[Math.ceil(rounds*.95)-1],result};}
const results=fixtures.map(f=>{const old=measure(baseline,f.obstacles),current=measure(optimized,f.obstacles);if(JSON.stringify(old.result)!==JSON.stringify(current.result))throw Error('Routing geometry regression: '+f.name);return {fixture:f.name,obstacles:f.obstacles.length,baselineMedianMs:old.medianMs,optimizedMedianMs:current.medianMs,baselineP95Ms:old.p95Ms,optimizedP95Ms:current.p95Ms,speedupMedian:old.medianMs/current.medianMs,geometryIdentical:true};});
const crossingFrom={x:0,y:0,w:30,h:30},crossingTo={x:300,y:0,w:30,h:30};
const existing=[{points:[{x:165,y:-100},{x:165,y:120}]}];
const selected=routeWithFewerCrossings(crossingFrom,crossingTo,existing);
const report={version:'26.7',environment:`Node.js ${process.version}; synthetic; NOT Windows graphical`,roundsPerVariant:rounds,results,crossingFixture:{crossings:countRouteCrossings([...existing,selected]),sharedLength:existing.reduce((n,r)=>n+routeSharedLength(r,selected),0),offset:selected.offset}};
writeFileSync('BENCHMARK-ROUTING-V26.7.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
