// OpenVisio v41.27 — bounded SVG DOM benchmark, per-case watchdog.
// Author: Abdelhalim Talbi. Simulated DOM, not a browser/Windows measurement.
import {spawnSync} from 'node:child_process';
import {writeFileSync} from 'node:fs';
const cases=[10,25,50,100];
const timeoutMs=Number(process.env.OV_SVG_TIMEOUT_MS||5000);
const results=[];
for(const size of cases){
 const start=performance.now();
 const child=spawnSync(process.execPath,[new URL('./benchmark-svg-v427-worker.mjs',import.meta.url).pathname,String(size)],{encoding:'utf8',timeout:timeoutMs,maxBuffer:1024*1024});
 let data=null;
 if(!child.error&&child.status===0){try{data=JSON.parse(child.stdout)}catch{}}
 results.push({size,status:data?'PASS':child.error?.code==='ETIMEDOUT'?'TIMEOUT':'ERROR',wallMs:+(performance.now()-start).toFixed(2),result:data?.results?.[0]||null,error:child.error?.code||null});
 console.log(`${size}: ${results.at(-1).status}`);
}
const report={version:'41.26',scope:'Synthetic JS DOM only; excludes browser layout/paint and Windows',timeoutMs,node:process.version,results};
writeFileSync(new URL('../../BENCHMARK-SVG-V41.27.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(results.some(x=>x.status!=='PASS'))process.exitCode=2;
