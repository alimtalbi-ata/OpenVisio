import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {spatialRoutingImpact} from '../src/spatial-routing.js';
import {routeEdge} from '../src/routing.js';
const rows=[];
for(const size of [100,500,1000]){
 const nodes=Array.from({length:size},(_,i)=>({id:`n${i}`,x:(i%40)*180,y:Math.floor(i/40)*120,w:70,h:40}));
 const edges=Array.from({length:size-1},(_,i)=>({id:`e${i}`,from:`n${i}`,to:`n${i+1}`,style:'orthogonal'}));
 const routes=new Map(edges.map(e=>[e.id,routeEdge(nodes[Number(e.from.slice(1))],nodes[Number(e.to.slice(1))],'orthogonal')]));
 const nextNodes=structuredClone(nodes);nextNodes[Math.floor(size/2)].x+=15;
 const samples=25;let impacted=0,localTotal=0,fullTotal=0;
 for(let i=0;i<samples;i++){
  let t=performance.now();const impact=spatialRoutingImpact({nodes,edges},{nodes:nextNodes,edges},routes);impacted=impact.changedEdges.size;
  for(const e of edges){if(!impact.changedEdges.has(e.id))continue;routeEdge(nextNodes[Number(e.from.slice(1))],nextNodes[Number(e.to.slice(1))],'orthogonal');}
  localTotal+=performance.now()-t;
  t=performance.now();for(const e of edges)routeEdge(nextNodes[Number(e.from.slice(1))],nextNodes[Number(e.to.slice(1))],'orthogonal');fullTotal+=performance.now()-t;
 }
 rows.push({nodes:size,edges:edges.length,impacted,localMeanMs:+(localTotal/samples).toFixed(3),fullMeanMs:+(fullTotal/samples).toFixed(3),samples});
}
const result={date:new Date().toISOString(),node:process.version,platform:process.platform,scope:'Synthetic Node.js geometry-only benchmark; excludes browser SVG, global routing heuristics, UI and cache serialization; timings vary by machine',rows};
writeFileSync(new URL('../BENCHMARK-V17.5.json',import.meta.url),JSON.stringify(result,null,2));console.table(rows);
