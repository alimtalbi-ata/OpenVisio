// Mesures synthétiques, sans interface graphique. Auteur : Abdelhalim Talbi
import {performance} from 'node:perf_hooks';
import {routeBounds,proposeRouteOffset} from '../src/route-preview.js';
const samples=[];
for(const count of [100,500,1000]){
 const nodes=Array.from({length:count},(_,i)=>({id:`n${i}`,x:(i%40)*140,y:Math.floor(i/40)*100,w:90,h:60}));
 const edges=Array.from({length:count-1},(_,i)=>({id:`e${i}`,from:`n${i}`,to:`n${i+1}`,style:'orthogonal'}));
 const routes=new Map(edges.map((e,i)=>[e.id,{points:[{x:nodes[i].x+90,y:nodes[i].y+30},{x:nodes[i+1].x,y:nodes[i+1].y+30}]}]));
 const t0=performance.now();for(const route of routes.values())routeBounds(route.points);const boundsMs=performance.now()-t0;
 const t1=performance.now();proposeRouteOffset(edges[0],nodes,routes,{maxLanes:2});const previewMs=performance.now()-t1;
 samples.push({nodes:count,edges:edges.length,boundsMs:+boundsMs.toFixed(3),previewMs:+previewMs.toFixed(3)});
}
console.log(JSON.stringify({kind:'synthetic-nodejs-not-ui',samples},null,2));
