// OpenVisio v30.9 — audit documentaire des chemins FC. Auteur : Abdelhalim Talbi.
import {traceSanPaths} from './san-path-trace-v307.js';
const clean=x=>String(x??'').trim();
const validWwpn=x=>/^(?:[0-9a-f]{2}:){7}[0-9a-f]{2}$/i.test(clean(x))||/^[0-9a-f]{16}$/i.test(clean(x));
export function auditFcTrace(trace){
 const findings=[];
 for(const [index,path] of (trace?.paths??[]).entries()){
  const hops=path.hops??[];const fabrics=new Set();
  for(const [i,h] of hops.entries()){
   const prefix={path:index+1,hop:i+1,edgeId:clean(h.edgeId)};
   for(const [key,value] of [['sourceWwpn',h.sourceWwpn],['targetWwpn',h.targetWwpn]])if(clean(value)&&!validWwpn(value))findings.push({...prefix,code:'WWPN_INVALID',severity:'P2',detail:key+' format non reconnu'});
   if(!clean(h.sourcePort)||!clean(h.targetPort))findings.push({...prefix,code:'PORT_MISSING',severity:'P3',detail:'Port source ou cible absent'});
   const fabric=clean(h.fabric).toUpperCase();if(fabric==='A'||fabric==='B')fabrics.add(fabric);else findings.push({...prefix,code:'FABRIC_UNKNOWN',severity:'P2',detail:'Fabric non renseignée ou non reconnue'});
   if(i>0){const previous=hops[i-1];if(clean(previous.to)!==clean(h.from))findings.push({...prefix,code:'PATH_DISCONTINUITY',severity:'P1',detail:'Sauts non contigus'});
    if(validWwpn(previous.targetWwpn)&&validWwpn(h.sourceWwpn)&&clean(previous.targetWwpn).replaceAll(':','').toLowerCase()!==clean(h.sourceWwpn).replaceAll(':','').toLowerCase())findings.push({...prefix,code:'WWPN_DISCONTINUITY',severity:'P2',detail:'WWPN non cohérents au nœud intermédiaire'});
   }
   if(h.isl&&(!clean(h.sourcePort)||!clean(h.targetPort)))findings.push({...prefix,code:'ISL_PORT_MISSING',severity:'P2',detail:'Ports ISL incomplets'});
  }
  if(fabrics.size>1)findings.push({path:index+1,hop:0,edgeId:'',code:'FABRIC_CROSSING',severity:'P1',detail:'Chemin traversant Fabric A et B'});
 }
 const counts={P1:0,P2:0,P3:0};for(const f of findings)counts[f.severity]++;
 return {findings,counts,complete:!trace?.truncated,disclaimer:'Audit de cohérence documentaire uniquement ; aucun zoning ou état physique vérifié.'};
}
export function auditFcDocument(doc,options){return auditFcTrace(traceSanPaths(doc,options));}
export function auditFcCsv(audit){const q=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[=+@\-\t\r]/,"'$&")+'"';return [['path','hop','edge','severity','code','detail'],...(audit?.findings??[]).map(f=>[f.path,f.hop,f.edgeId,f.severity,f.code,f.detail])].map(row=>row.map(q).join(',')).join('\r\n')+'\r\n';}
