// OpenVisio v13.7 — analyse déclarative des impacts SAN. Auteur : Abdelhalim Talbi.
import {validateTopology,diffTopologies} from './topology-diff.js';
import {auditSanPaths} from './san-audit.js';
const rank={unreachable:0,'at-risk':1,redundant:2};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function compareSanConnectivity(before,after){
 validateTopology(before);validateTopology(after);
 const old=auditSanPaths(before.nodes,before.edges),now=auditSanPaths(after.nodes,after.edges);
 const oldMap=new Map(old.map(x=>[JSON.stringify([x.sourceId,x.targetId]),x]));
 const newMap=new Map(now.map(x=>[JSON.stringify([x.sourceId,x.targetId]),x]));
 const pairs=[...new Set([...oldMap.keys(),...newMap.keys()])].sort();
 const findings=pairs.map(key=>{const a=oldMap.get(key),b=newMap.get(key);const from=a?.status||'absent',to=b?.status||'absent';
 const impact=!a?'new-pair':!b?'removed-pair':rank[to]<rank[from]?'degraded':rank[to]>rank[from]?'improved':'stable';
 const lostFabrics=a&&b?['A','B'].filter(f=>a['has'+f]&&!b['has'+f]):[];
 return {sourceId:(b||a).sourceId,targetId:(b||a).targetId,sourceName:(b||a).sourceName,targetName:(b||a).targetName,before:from,after:to,impact,lostFabrics,oldPaths:a?.paths??0,newPaths:b?.paths??0,spof:b?.spof||[]};});
 const changes=diffTopologies(before,after);
 const affectedIds=new Set(changes.filter(x=>x.status!=='added').map(x=>x.id));
 const critical=findings.filter(x=>x.impact==='degraded'||x.impact==='removed-pair');
 return {findings,critical,changes,affectedIds:[...affectedIds],summary:{pairs:findings.length,degraded:critical.length,improved:findings.filter(x=>x.impact==='improved').length,stable:findings.filter(x=>x.impact==='stable').length}};
}
export function sanImpactHtml(result){const rows=result.findings.map(x=>`<tr class="${esc(x.impact)}"><td>${esc(x.sourceName)} → ${esc(x.targetName)}</td><td>${esc(x.before)}</td><td>${esc(x.after)}</td><td>${esc(x.impact)}</td><td>${esc(x.lostFabrics.join(', ')||'—')}</td><td>${esc(x.oldPaths)} → ${esc(x.newPaths)}</td></tr>`).join('');return `<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Impact SAN</title><style>body{font:15px system-ui;margin:2rem;color:#183047}table{border-collapse:collapse;width:100%}td,th{border:1px solid #cad3dc;padding:.6rem;text-align:left}.degraded,.removed-pair{background:#ffe0e0}.improved{background:#dcf6e5}</style><h1>Analyse comparative des chemins SAN</h1><p>Auteur : Abdelhalim Talbi</p><p>Analyse déclarative des liaisons Fibre Channel et des Fabrics A/B, sans découverte ni validation sur équipements réels. Une absence de chemin dans le diagramme ne prouve pas une panne réelle.</p><p>${result.summary.degraded} paire(s) dégradée(s) ou supprimée(s) ; ${result.summary.improved} améliorée(s).</p><table><thead><tr><th>Serveur → Stockage</th><th>Avant</th><th>Après</th><th>Impact</th><th>Fabrics perdues</th><th>Chemins</th></tr></thead><tbody>${rows}</tbody></table></html>`;}
