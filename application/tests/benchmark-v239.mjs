// Benchmark reproductible des contrôles géométriques SAN — OpenVisio v23.9.
// Auteur : Abdelhalim Talbi. Mesure Node.js, pas de performance Windows UI.
import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {compareRoutingGeometry} from '../src/renderer.js';
import {buildRouteSpatialIndex,queryRouteSpatialIndex,routeIntersectsZone} from '../src/spatial-routing.js';
const sizes=[64,256,1024];
const repeats=80;
const results=[];
for(const count of sizes){
 const routes=new Map();
 for(let i=0;i<count;i++){
  const x=(i%32)*150,y=Math.floor(i/32)*90;
  routes.set(`SAN-${i}`,{points:[{x,y},{x:x+40,y},{x:x+40,y:y+25},{x:x+90,y:y+25}]});
 }
 const clone=new Map(routes);
 const divergent=new Map(routes);
 const mid=`SAN-${Math.floor(count/2)}`;
 const original=routes.get(mid);
 divergent.set(mid,{points:original.points.map((p,i)=>i===2?{...p,y:p.y+2}:p)});
 const zone={left:150,top:0,right:230,bottom:45};
 const index=buildRouteSpatialIndex(routes);
 const candidates=queryRouteSpatialIndex(index,[zone]);
 const exact=[...candidates].filter(id=>routeIntersectsZone(routes.get(id),zone));
 const base=compareRoutingGeometry(routes,clone),different=compareRoutingGeometry(routes,divergent);
 if(!base.equivalent||different.equivalent||different.divergentEdges.join()!==mid)throw Error('Benchmark correctness check failed');
 const time=(fn)=>{const start=performance.now();for(let i=0;i<repeats;i++)fn();return Number(((performance.now()-start)/repeats).toFixed(5));};
 const equalityMs=time(()=>compareRoutingGeometry(routes,clone));
 const divergenceMs=time(()=>compareRoutingGeometry(routes,divergent));
 const spatialMs=time(()=>queryRouteSpatialIndex(index,[zone]));
 results.push({edges:count,repeats,equalityMs,divergenceMs,spatialQueryMs:spatialMs,spatialCandidates:candidates.size,spatialExact:exact.length,divergences: different.divergentEdges.length});
}
const report={version:'23.9',environment:{runtime:process.version,platform:process.platform,arch:process.arch},method:'80 repetitions; mean elapsed milliseconds per call; synthetic SAN orthogonal routes; timings indicative, not Windows UI',results};
writeFileSync(new URL('../BENCHMARK-V23.9.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
