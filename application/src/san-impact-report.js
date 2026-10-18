// OpenVisio v29.0 — rapport de simulation documentaire. Auteur : Abdelhalim Talbi.
import {simulateSanFailure} from './san-failure-simulation.js';
const signature=p=>JSON.stringify([p.serverId,p.storageId,p.nodeIds,p.edgeIds]);
export function buildSanImpactReport(doc,options={}) {
 const simulation=simulateSanFailure(doc,options);
 const before=simulation.before.paths, after=simulation.after.paths;
 const surviving=new Set(after.map(signature));
 const lost=before.filter(p=>!surviving.has(signature(p)));
 const preserved=before.filter(p=>surviving.has(signature(p)));
 const affected=simulation.affected.filter(a=>a.lost>0);
 const disconnected=affected.filter(a=>a.unreachable);
 const remainingRedundancy=simulation.after.resilience.filter(r=>r.issues.length);
 return {version:'29.0',mode:'documentary',failure:{nodeId:options.failedNodeId??null,fabric:options.failedFabric??null},summary:{pathsBefore:before.length,pathsAfter:after.length,lostPaths:lost.length,preservedPaths:preserved.length,affectedPairs:affected.length,disconnectedPairs:disconnected.length,remainingRedundancyWarnings:remainingRedundancy.length},visual:{lostEdgeIds:[...new Set(lost.flatMap(p=>p.edgeIds))].sort(),preservedEdgeIds:[...new Set(preserved.flatMap(p=>p.edgeIds))].sort(),lostNodeIds:[...new Set(lost.flatMap(p=>p.nodeIds))].sort()},affected,remainingRedundancy,truncated:simulation.truncated,warning:'Simulation documentaire non destructive. Une limite de parcours peut rendre les résultats incomplets. Ne prouve pas le multipathing réel.'};
}
export function sanImpactCsv(report){
 const escape=v=>'"'+String(v??'').replace(/^[=+@\-\t\r]/,m=>'\''+m).replaceAll('"','""')+'"';
 return ['server_id,storage_id,paths_before,paths_after,paths_lost,unreachable',...report.affected.map(a=>[a.serverId,a.storageId,a.before,a.after,a.lost,a.unreachable].map(escape).join(','))].join('\n');
}
