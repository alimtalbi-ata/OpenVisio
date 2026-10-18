import {performance} from 'node:perf_hooks';
import {resolveDistributedRoute} from '../src/renderer.js';
const results=[];
for(const size of [64,256,1024]){
 const nodes=Array.from({length:size},(_,i)=>({id:`n${i}`,x:i*10,y:0}));
 const edges=Array.from({length:size},(_,i)=>({id:`e${i}`,style:'avoid'}));
 const routes=new Map(edges.map(e=>[e.id,{points:[{x:0,y:0}],path:'M 0 0'}]));
 const rounds=80;
 const start=performance.now();let fallback=0;
 for(let r=0;r<rounds;r++)for(const edge of edges)resolveDistributedRoute(edge,nodes[0],nodes[1],nodes,routes,[],()=>{fallback++;return null});
 const cachedMs=(performance.now()-start)/rounds;
 const missing=new Map(routes);missing.delete(edges[0].id);
 const t2=performance.now();for(let r=0;r<rounds;r++)resolveDistributedRoute(edges[0],nodes[0],nodes[1],nodes,missing,[],()=>{fallback++;return {points:[]}});
 const missingMs=(performance.now()-t2)/rounds;
 results.push({edges:size,mean_cached_routes_ms:Number(cachedMs.toFixed(5)),mean_missing_route_ms:Number(missingMs.toFixed(5)),fallback_calls:fallback});
}
console.log(JSON.stringify({environment:'Node.js/Linux, microbenchmark sans DOM navigateur',iterations:80,results},null,2));
