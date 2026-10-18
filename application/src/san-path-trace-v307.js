// OpenVisio v30.7 — traçabilité documentaire FC. Auteur : Abdelhalim Talbi.
import {exploreSanPaths} from './san-path-explorer.js';
const value=x=>String(x??'').trim();
const port=e=>({sourcePort:value(e.fromPort??e.sourcePort),targetPort:value(e.toPort??e.targetPort),sourceWwpn:value(e.fromWwpn??e.sourceWwpn),targetWwpn:value(e.toWwpn??e.targetWwpn)});
export function traceSanPaths(doc,{serverId,storageId,maxDepth=12,maxPaths=500}={}){
 const result=exploreSanPaths(doc,{maxDepth,maxPaths});
 const edges=new Map((Array.isArray(doc?.edges)?doc.edges:[]).filter(e=>e&&e.id!=null).map(e=>[value(e.id),e]));
 const nodes=new Map((Array.isArray(doc?.nodes)?doc.nodes:[]).filter(n=>n&&n.id!=null).map(n=>[value(n.id),n]));
 const paths=result.paths.filter(p=>(serverId==null||p.serverId===value(serverId))&&(storageId==null||p.storageId===value(storageId))).map(p=>{
  const hops=p.edgeIds.map((id,i)=>{const e=edges.get(id);const from=p.nodeIds[i],to=p.nodeIds[i+1];if(!e)return {edgeId:id,from,to,issues:['EDGE_NOT_FOUND']};
   const forward=value(e.from)===from&&value(e.to)===to;const backward=value(e.to)===from&&value(e.from)===to;
   const meta=port(e);const sourcePort=forward?meta.sourcePort:meta.targetPort,targetPort=forward?meta.targetPort:meta.sourcePort;
   const sourceWwpn=forward?meta.sourceWwpn:meta.targetWwpn,targetWwpn=forward?meta.targetWwpn:meta.sourceWwpn;
   const issues=[...(!forward&&!backward?['DIRECTION_UNVERIFIED']:[]),...(!sourcePort||!targetPort?['PORT_METADATA_MISSING']:[]),...(!sourceWwpn||!targetWwpn?['WWPN_METADATA_MISSING']:[])];
   const fromType=value(nodes.get(from)?.type).toLowerCase(),toType=value(nodes.get(to)?.type).toLowerCase();
   return {edgeId:id,from,to,fromType,toType,sourcePort,targetPort,sourceWwpn,targetWwpn,fabric:value(e.fabric??e.sanFabric).toUpperCase()||'UNKNOWN',isl:['switch','san-switch','fc-switch'].includes(fromType)&&['switch','san-switch','fc-switch'].includes(toType),issues};
  });
  return {...p,hops,traceIssues:[...new Set([...p.issues,...hops.flatMap(h=>h.issues)])].sort()};
 });
 return {paths,truncated:result.truncated,warning:'Topologie déclarative uniquement : WWPN, ports et ISL non découverts automatiquement.'};
}
export function pathTraceCsv(trace){const escape=v=>'"'+String(v??'').replaceAll('"','""').replace(/^[=+@\-\t\r]/,"'$&")+'"';const rows=[['server','storage','path','hop','edge','from','to','source_port','target_port','source_wwpn','target_wwpn','fabric','isl','issues']];for(const [i,p] of (trace?.paths??[]).entries())for(const [j,h] of p.hops.entries())rows.push([p.serverId,p.storageId,i+1,j+1,h.edgeId,h.from,h.to,h.sourcePort,h.targetPort,h.sourceWwpn,h.targetWwpn,h.fabric,h.isl,h.issues.join(';')]);return rows.map(r=>r.map(escape).join(',')).join('\r\n')+'\r\n';}
