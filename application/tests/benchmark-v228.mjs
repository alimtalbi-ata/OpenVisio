import {performance} from 'node:perf_hooks';
import {analyzeDenseRouteBundles} from '../src/routing.js';
const scenarios={
 sparse:n=>new Map(Array.from({length:n},(_,i)=>[String(i),{points:[{x:i*25,y:0},{x:i*25+12,y:0}]}])),
 parallel:n=>new Map(Array.from({length:n},(_,i)=>[String(i),{points:[{x:0,y:i*8},{x:900,y:i*8}]}])),
 dense:n=>new Map(Array.from({length:n},(_,i)=>[String(i),{points:[{x:0,y:i%25*8},{x:900,y:i%25*8}]}]))
};
for(const [scenario,create] of Object.entries(scenarios))for(const count of [100,300,600]){
 const routes=create(count);for(let warm=0;warm<3;warm++)analyzeDenseRouteBundles(routes);
 const times=[];let report;for(let run=0;run<7;run++){const start=performance.now();report=analyzeDenseRouteBundles(routes);times.push(performance.now()-start)}
 times.sort((a,b)=>a-b);console.log(JSON.stringify({scenario,count,medianMs:Number(times[3].toFixed(3)),p90Ms:Number(times[6].toFixed(3)),pairsChecked:report.pairsChecked,findings:report.issues.length,complete:report.complete}));
}
