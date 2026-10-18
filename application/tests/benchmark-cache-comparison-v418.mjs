// OpenVisio v41.18 — comparative synthetic cache benchmark. Auteur : Abdelhalim Talbi.
import {performance} from 'node:perf_hooks';
import {createRouteValueCache} from '../src/route-cache.js';
const samples=[];
for(const count of [100,500,1000]){
 for(const mode of ['full-clear','targeted-delete']){
  const iterations=15, elapsed=[];let remaining=0;
  for(let run=0;run<iterations;run++){
   const cache=createRouteValueCache({limit:count+1});
   for(let i=0;i<count;i++)cache.set(`san-link-${i}`,{points:[{x:i,y:0},{x:i+1,y:50}]});
   const start=performance.now();
   if(mode==='full-clear')cache.clear();
   else for(let i=0;i<count;i+=2)cache.delete(`san-link-${i}`);
   elapsed.push(performance.now()-start);remaining=cache.stats().size;
  }
  elapsed.sort((x,y)=>x-y);
  samples.push({routes:count,mode,medianMs:Number(elapsed[7].toFixed(4)),remainingRoutes:remaining,iterations});
 }
}
console.log(JSON.stringify({version:'41.18',type:'synthetic Node.js cache operation comparison; not Windows UI nor actual SAN diagram rendering',node:process.version,samples},null,2));
