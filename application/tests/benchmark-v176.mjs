import {performance} from 'node:perf_hooks';
import {buildRouteSpatialIndex,queryRouteSpatialIndex,routeIntersectsZone,routeBounds} from '../src/spatial-routing.js';
const out=[];
for(const count of [100,500,1000,5000]){
 const routes=new Map();for(let i=0;i<count;i++){const x=(i%100)*100,y=Math.floor(i/100)*100;routes.set('e'+i,{points:[{x,y},{x:x+40,y:y+40}]});}
 const index=buildRouteSpatialIndex(routes),zones=Array.from({length:50},(_,i)=>({left:(i%10)*100+10,right:(i%10)*100+25,top:10,bottom:25}));
 let hits=0;const t0=performance.now();for(const z of zones)for(const [id,r] of routes)if(routeIntersectsZone(r,z))hits++;const baselineMs=performance.now()-t0;
 let indexedHits=0;const t1=performance.now();for(const z of zones)for(const id of queryRouteSpatialIndex(index,[z]))if(routeIntersectsZone(routes.get(id),z))indexedHits++;const indexedMs=performance.now()-t1;
 if(hits!==indexedHits)throw Error(`mismatch ${count}: ${hits} ${indexedHits}`);
 out.push({routes:count,queries:zones.length,baselineMs:+baselineMs.toFixed(3),indexedMs:+indexedMs.toFixed(3),matches:hits});
}
console.log(JSON.stringify(out,null,2));
