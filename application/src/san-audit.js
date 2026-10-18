// Auteur : Abdelhalim Talbi — audit topologique déclaratif SAN v12.1.
import {interfaceFamily} from './ports.js';
const fabric=n=>String(n?.fabric||'').trim().toUpperCase();
const fc=e=>interfaceFamily(e.sourceInterface)==='fibre-channel'&&interfaceFamily(e.targetInterface)==='fibre-channel';
export function auditSanPaths(nodes,edges){
 const byId=new Map(nodes.map(n=>[n.id,n]));
 const adjacency=new Map(nodes.map(n=>[n.id,[]]));
 for(const e of edges){if(!fc(e)||!byId.has(e.from)||!byId.has(e.to))continue;adjacency.get(e.from).push({id:e.to,edge:e.id});adjacency.get(e.to).push({id:e.from,edge:e.id});}
 const servers=nodes.filter(n=>n.type==='server'),storages=nodes.filter(n=>n.type==='storage');
 const results=[];
 for(const source of servers)for(const target of storages){
  const paths=[];
  for(const f of ['A','B']){
   const queue=[{id:source.id,nodes:[source.id],edges:[]}];
   let steps=0;
   while(queue.length&&steps++<5000&&paths.filter(p=>p.fabric===f).length<32){
    const cur=queue.shift();
    if(cur.id===target.id){if(cur.edges.length>=2)paths.push({...cur,fabric:f});continue;}
    if(cur.nodes.length>=Math.min(nodes.length,12))continue;
    for(const next of adjacency.get(cur.id)||[]){if(cur.nodes.includes(next.id))continue;const node=byId.get(next.id);if(next.id!==target.id&&next.id!==source.id&&fabric(node)!==f)continue;queue.push({id:next.id,nodes:[...cur.nodes,next.id],edges:[...cur.edges,next.edge]});}
   }
  }
  const a=paths.filter(p=>p.fabric==='A'),b=paths.filter(p=>p.fabric==='B');
  const distinct=a.some(x=>b.some(y=>!x.nodes.slice(1,-1).some(id=>y.nodes.slice(1,-1).includes(id))&&!x.edges.some(id=>y.edges.includes(id))));
  const internal=[...new Set(paths.flatMap(p=>p.nodes.slice(1,-1)))];
  const spof=internal.filter(id=>paths.length>0&&paths.every(p=>p.nodes.includes(id)));
  results.push({sourceId:source.id,sourceName:source.title||source.id,targetId:target.id,targetName:target.title||target.id,hasA:a.length>0,hasB:b.length>0,independent:distinct,paths:paths.length,spof, status:distinct?'redundant':paths.length?'at-risk':'unreachable'});
 }
 return results;
}
export function zoningReview(nodes,edges){
 const byId=new Map(nodes.map(n=>[n.id,n]));const findings=[];
 for(const e of edges){if(!fc(e))continue;const a=byId.get(e.from),b=byId.get(e.to);if(!a||!b)continue;
  if(a.type==='server'&&b.type==='storage'||a.type==='storage'&&b.type==='server')findings.push({edgeId:e.id,code:'direct-fc-link-review'});
  if(a.type==='switch'&&b.type==='switch'&&fabric(a)&&fabric(b)&&fabric(a)!==fabric(b))findings.push({edgeId:e.id,code:'cross-fabric-switch-link'});
 }
 return findings;
}
