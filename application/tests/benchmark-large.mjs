import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {generateTopology} from '../src/benchmark.js';
import {optimizeConnectionOrder,routeEdge} from '../src/routing.js';
const results=[];
for(const size of [100,500,1000]){
 const {nodes,edges}=generateTopology(size);
 const route=(e,a,b)=>routeEdge(a,b,'orthogonal');
 const start=performance.now();
 const result=optimizeConnectionOrder(edges,nodes,route);
 results.push({nodes:size,edges:edges.length,elapsedMs:+(performance.now()-start).toFixed(2),routes:result.routes.size,crossingsEvaluated:result.crossingsEvaluated});
}
const report={date:new Date().toISOString(),environment:{node:process.version,platform:process.platform,arch:process.arch},scope:'Node.js routing optimizer with orthogonal links; excludes SVG DOM, smart obstacle search, browser UI',results};
writeFileSync(new URL('../BENCHMARK-V16.9.json',import.meta.url),JSON.stringify(report,null,2));
console.table(results);
