// OpenVisio v29.8 — indépendance Fabric A/B documentaire. Auteur : Abdelhalim Talbi.
import {exploreSanPaths} from './san-path-explorer.js';
export function analyzeSharedTransit(documentModel){
 const result=exploreSanPaths(documentModel,{maxDepth:10,maxPaths:300});
 const findings=[];
 const groups=new Map();
 for(const path of result.paths){
  if(path.fabrics.length!==1||!['A','B'].includes(path.fabrics[0]))continue;
  const key=JSON.stringify([path.serverId,path.storageId]);
  if(!groups.has(key))groups.set(key,{A:[],B:[]});groups.get(key)[path.fabrics[0]].push(path);
 }
 for(const [pair,group] of groups){
  if(!group.A.length||!group.B.length)continue;
  const [serverId,storageId]=JSON.parse(pair);
  const allA=new Set(group.A.flatMap(p=>[...p.switches,...p.edgeIds]));
  const allB=new Set(group.B.flatMap(p=>[...p.switches,...p.edgeIds]));
  const shared=[...allA].filter(id=>allB.has(id)).sort();
  const independent=group.A.some(a=>group.B.some(b=>!a.switches.some(id=>b.switches.includes(id))&&!a.edgeIds.some(id=>b.edgeIds.includes(id))));
  for(const id of shared)findings.push({serverId,storageId,componentId:id,classification:independent?'SHARED_BUT_ALTERNATIVE_EXISTS':'POTENTIAL_COMMON_TRANSIT',recommendation:'Contrôler les chemins physiques indépendants, les alimentations et le zoning ; vérifier le multipathing réel.'});
 }
 return {findings:findings.sort((a,b)=>a.serverId.localeCompare(b.serverId)||a.storageId.localeCompare(b.storageId)||a.componentId.localeCompare(b.componentId)),truncated:result.truncated,scope:result.scope};
}
