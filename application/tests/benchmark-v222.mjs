import {performance} from 'node:perf_hooks';
import {diagnoseRouteTopology} from '../src/routing.js';
for(const count of [100,300,600]){
 const routes=new Map(Array.from({length:count},(_,i)=>[String(i),{points:[{x:0,y:i*12},{x:800,y:i*12}]}]));
 const start=performance.now();const report=diagnoseRouteTopology(routes);console.log(JSON.stringify({count,elapsedMs:Number((performance.now()-start).toFixed(3)),...report}));
}
