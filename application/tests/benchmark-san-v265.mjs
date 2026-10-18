import {readFileSync,writeFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {proposeSanAlternate} from '../src/san-alternate-routes.js';
const fixture=JSON.parse(readFileSync(new URL('../fixtures/san-astar-multiwall-v265.json',import.meta.url)));
const samples=[];for(let i=0;i<30;i++){const nodes=structuredClone(fixture.nodes),edges=structuredClone(fixture.edges),routes=new Map(Object.entries(structuredClone(fixture.routes)));const start=performance.now();const proposal=proposeSanAlternate(edges[0],nodes,routes,edges,{steps:[10]});samples.push({ms:performance.now()-start,status:proposal.status,collisions:proposal.after?.collisions??null});}
const times=samples.map(s=>s.ms).sort((a,b)=>a-b);const report={version:'26.5',runs:samples.length,medianMs:times[14],p95Ms:times[28],maxMs:times.at(-1),statuses:Object.fromEntries([...new Set(samples.map(s=>s.status))].map(k=>[k,samples.filter(s=>s.status===k).length])),environment:'Node.js; synthetic fixtures; not Windows UI'};
writeFileSync('BENCHMARK-SAN-V26.5.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
