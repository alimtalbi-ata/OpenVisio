// OpenVisio v30.6 — scénarios par identifiant de connexion. Auteur : Abdelhalim Talbi.
import {exploreSanPaths} from './san-path-explorer.js';
const unique=items=>[...new Set(items.filter(x=>typeof x==='string'&&x.trim()))].sort();
export function buildPathFailureOverlay(doc,serverId,storageId,failedFabric,options={}){
 if(!['A','B'].includes(failedFabric))throw new RangeError('Fabric A ou B requise');
 const result=exploreSanPaths(doc,options);
 const relevant=result.paths.filter(p=>p.serverId===serverId&&p.storageId===storageId);
 const lost=relevant.filter(p=>p.fabrics.includes(failedFabric));
 const surviving=relevant.filter(p=>p.fabrics.length===1&&p.fabrics[0]!==failedFabric);
 const ambiguous=relevant.filter(p=>p.fabrics.length!==1||p.fabrics[0]==='UNKNOWN');
 const lostIds=unique(lost.flatMap(p=>p.edgeIds));
 const survivingIds=unique(surviving.flatMap(p=>p.edgeIds));
 const sharedIds=unique([...lostIds.filter(id=>survivingIds.includes(id)),...lost.flatMap(p=>p.switches).filter(id=>surviving.some(p=>p.switches.includes(id)))]);
 const shared=new Set(sharedIds);
 return {lostIds:lostIds.filter(id=>!shared.has(id)),survivingIds:survivingIds.filter(id=>!shared.has(id)),sharedIds,ambiguousIds:unique(ambiguous.flatMap(p=>p.edgeIds)),summary:{baseline:relevant.length,lost:lost.length,surviving:surviving.length,ambiguous:ambiguous.length,truncated:result.truncated},warning:result.truncated?'Exploration tronquée : résultats incomplets.':'Simulation documentaire, sans validation du multipathing réel.'};
}
