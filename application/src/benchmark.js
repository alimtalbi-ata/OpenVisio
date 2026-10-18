// Auteur : Abdelhalim Talbi
import {routeEdge,routeAvoidingObstacles} from "./routing.js";
export function generateTopology(count){
 if(!Number.isInteger(count)||count<2||count>10000)throw new RangeError("count must be 2..10000");
 const cols=Math.ceil(Math.sqrt(count));
 const nodes=Array.from({length:count},(_,i)=>({id:`node-${i}`,x:(i%cols)*220,y:Math.floor(i/cols)*130,w:150,h:74,title:`Serveur ${i}`}));
 const edges=Array.from({length:count-1},(_,i)=>({id:`edge-${i}`,from:nodes[i].id,to:nodes[i+1].id,style:"orthogonal"}));
 return {nodes,edges};
}
export function benchmarkRoutes(count,now=()=>performance.now()){
 const {nodes,edges}=generateTopology(count),byId=new Map(nodes.map(n=>[n.id,n]));
 const start=now();
 let pathBytes=0;
 for(const e of edges){
  const result=routeEdge(byId.get(e.from),byId.get(e.to),e.style);
  pathBytes+=result.path.length;
 }
 const elapsedMs=now()-start;
 return {nodes:nodes.length,edges:edges.length,elapsedMs,pathBytes,meanRouteMs:elapsedMs/edges.length};
}
