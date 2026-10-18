import {performance} from 'node:perf_hooks';
import {writeFileSync} from 'node:fs';
import {reduceFanOutCrossings as optimized} from '../src/routing.js';
import {reduceFanOutCrossings as reference} from '../src/routing-legacy-benchmark.js';
const scenarios=['ladder','dense','parallel'], sizes=[20,50,100], reps=3;
const median=a=>[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)];
function fixture(n,kind){const nodes=[],edges=[],routes=new Map();for(let i=0;i<=n;i++)nodes.push({id:`n${i}`,x:(i%20)*95,y:Math.floor(i/20)*110,width:55,height:35});for(let i=0;i<n;i++){const id=`e${i}`,x=(i%20)*95+55,y=Math.floor(i/20)*110+17,dy=kind==='dense'?((i*7)%11-5)*23:kind==='parallel'?(i%4)*8:((i%5)-2)*30;const points=[{x,y},{x:x+12,y},{x:x+12,y:y+dy},{x:x+65,y:y+dy},{x:x+65,y:y+dy+10}];edges.push({id,from:`n${i}`,to:`n${i+1}`});routes.set(id,{points,orthogonalFanOut:true,path:points.map((p,j)=>`${j?'L':'M'} ${p.x} ${p.y}`).join(' ')});}return {nodes,edges,routes};}
const results=[];
for (const scenario of scenarios) for (const n of sizes) {
 const f=fixture(n,scenario), times={reference:[],optimized:[]}; let same=true;
 for(let i=0;i<reps;i++) {
  const outputs={};
  const order=i%2 ? [['optimized',optimized],['reference',reference]] : [['reference',reference],['optimized',optimized]];
  for(const [name,fn] of order){const start=performance.now();outputs[name]=fn(f.edges,f.routes,f.nodes);times[name].push(performance.now()-start);}
  for(const [id,r] of outputs.reference){const other=outputs.optimized.get(id);if(JSON.stringify(r?.points)!==JSON.stringify(other?.points)||r?.path!==other?.path){same=false;break;}}
 }
 const result={scenario,edges:n,reference_ms:+median(times.reference).toFixed(3),optimized_ms:+median(times.optimized).toFixed(3),equivalent:same};
 results.push(result); console.log(JSON.stringify(result));
}
const report={version:'41.36',node:process.version,repetitions:reps,environment:'synthetic Node.js; not browser or Windows',results};writeFileSync('../BENCHMARK-CROSSINGS-V41.36.json',JSON.stringify(report,null,2));if(results.some(r=>!r.equivalent))process.exitCode=1;
