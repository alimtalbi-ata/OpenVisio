import {performance} from 'node:perf_hooks';
import {createRouteValueCache} from '../src/route-cache.js';
// Synthetic cache microbenchmark; NOT a WebView2 rendering benchmark.
const results=[];
for(const n of [100,500,1000]){
 const cache=createRouteValueCache({limit:n});
 const routes=Array.from({length:n},(_,i)=>({points:Array.from({length:8},(_,j)=>({x:i+j,y:i-j}))}));
 const t0=performance.now();for(let i=0;i<n;i++)cache.set('route-'+i,routes[i]);const fill=performance.now()-t0;
 const t1=performance.now();for(let i=0;i<n*3;i++)cache.get('route-'+(i%n));const read=performance.now()-t1;
 const t2=performance.now();for(let i=0;i<n;i+=2)cache.delete('route-'+i);const invalidate=performance.now()-t2;
 results.push({routes:n,fill_ms:+fill.toFixed(3),read_3x_ms:+read.toFixed(3),invalidate_half_ms:+invalidate.toFixed(3),...cache.stats()});
}
console.log(JSON.stringify({kind:'synthetic-node-cache-microbenchmark',node:process.version,results},null,2));
