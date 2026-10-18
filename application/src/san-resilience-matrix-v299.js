// OpenVisio v29.9 — matrice de résilience documentaire. Auteur : Abdelhalim Talbi.
import {exploreSanPaths} from './san-path-explorer.js';
import {analyzeSharedTransit} from './san-spof-v298.js';
const id=x=>String(x??'');
export function buildResilienceMatrix(documentModel,options={}){
 const exploration=exploreSanPaths(documentModel,{maxDepth:options.maxDepth??10,maxPaths:options.maxPaths??300});
 const dependencies=analyzeSharedTransit(documentModel);
 const rows=exploration.resilience.map(pair=>{
  const shared=dependencies.findings.filter(x=>x.serverId===pair.serverId&&x.storageId===pair.storageId);
  const dangerous=shared.filter(x=>x.classification==='POTENTIAL_COMMON_TRANSIT');
  const severity=pair.fabricA===0||pair.fabricB===0?'P1':!pair.disjointDocumented||dangerous.length?'P2':shared.length?'P3':'P4';
  const recommendations=[...(!pair.fabricA||!pair.fabricB?['Documenter et vérifier un chemin sur chaque Fabric A/B']:[]),...(!pair.disjointDocumented?['Vérifier l’indépendance des switches et liaisons FC']:[]),...(dangerous.length?['Éliminer ou justifier les points de transit communs']:[])];
  return {serverId:pair.serverId,storageId:pair.storageId,fabricA:pair.fabricA,fabricB:pair.fabricB,paths:pair.pathCount,independentDocumented:pair.disjointDocumented,sharedTransitIds:[...new Set(shared.map(x=>x.componentId))].sort(),priority:severity,recommendations,issues:pair.issues};
 }).sort((a,b)=>a.priority.localeCompare(b.priority)||a.serverId.localeCompare(b.serverId)||a.storageId.localeCompare(b.storageId));
 return {rows,truncated:exploration.truncated||dependencies.truncated,scope:exploration.scope,summary:{total:rows.length,byPriority:Object.fromEntries(['P1','P2','P3','P4'].map(p=>[p,rows.filter(r=>r.priority===p).length]))}};
}
export function exportResilienceCsv(matrix){
 const safe=x=>{let s=id(x);if(/^[\s]*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
 const lines=[['server','storage','fabricA','fabricB','priority','sharedTransit','recommendations'].map(safe).join(',')];
 for(const r of matrix.rows||[])lines.push([r.serverId,r.storageId,r.fabricA,r.fabricB,r.priority,r.sharedTransitIds.join(';'),r.recommendations.join(';')].map(safe).join(','));
 return lines.join('\r\n')+'\r\n';
}
