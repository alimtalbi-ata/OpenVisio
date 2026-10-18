// OpenVisio v13.9 — matrice d’impact SAN déclarative. Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {auditSanPaths} from './san-audit.js';
import {applicationImpact,compareFcPorts} from './san-port-impact.js';
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function buildSanImpactMatrix(before,after){
 validateTopology(before);validateTopology(after);
 const previous=new Map(auditSanPaths(before.nodes,before.edges).map(p=>[JSON.stringify([p.sourceId,p.targetId]),p]));
 const current=new Map(auditSanPaths(after.nodes,after.edges).map(p=>[JSON.stringify([p.sourceId,p.targetId]),p]));
 const apps=applicationImpact(before,after), ports=compareFcPorts(before,after);
 const appMap=new Map();for(const a of apps)for(const id of a.servers){if(!appMap.has(id))appMap.set(id,[]);appMap.get(id).push(a.applicationName);}
 const rows=[...new Set([...previous.keys(),...current.keys()])].sort().map(key=>{
  const old=previous.get(key),now=current.get(key),p=now||old;
  const beforeStatus=old?.status||'absent',afterStatus=now?.status||'absent';
  const rank={'absent':0,'unreachable':1,'at-risk':2,'redundant':3};
  const status=!old?'new':!now?'removed':rank[afterStatus]<rank[beforeStatus]?'degraded':rank[afterStatus]>rank[beforeStatus]?'improved':'unchanged';
  const changedPorts=ports.rows.filter(x=>x.nodeId===p.sourceId&&x.status!=='stable').map(x=>x.port+' ('+x.status+')');
  return {serverId:p.sourceId,server:p.sourceName,storageId:p.targetId,storage:p.targetName,applications:appMap.get(p.sourceId)||[],before:beforeStatus,after:afterStatus,fabricBefore:old?['A','B'].filter(f=>old['has'+f]):[],fabricAfter:now?['A','B'].filter(f=>now['has'+f]):[],pathsBefore:old?.paths||0,pathsAfter:now?.paths||0,changedPorts,status,priority:status==='removed'||status==='degraded'?'high':status==='new'||status==='improved'?'info':'none'};
 });
 return {rows,summary:{total:rows.length,high:rows.filter(x=>x.priority==='high').length,affectedApplications:[...new Set(rows.filter(x=>x.priority==='high').flatMap(x=>x.applications))].length},scope:'Topologie déclarée uniquement : aucun contrôle de zoning actif, de multipathing OS ou de disponibilité applicative.'};
}
export function sanImpactMatrixCsv(matrix){
 const q=v=>{let s=String(v??'');if(/^[\s]*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
 return [['Serveur','Stockage','Applications','Avant','Après','Fabrics avant','Fabrics après','Chemins avant','Chemins après','Ports modifiés','Écart','Priorité'],...matrix.rows.map(r=>[r.server,r.storage,r.applications.join('; '),r.before,r.after,r.fabricBefore.join('/'),r.fabricAfter.join('/'),r.pathsBefore,r.pathsAfter,r.changedPorts.join('; '),r.status,r.priority])].map(r=>r.map(q).join(',')).join('\r\n')+'\r\n';
}
export function sanImpactMatrixHtml(matrix){const rows=matrix.rows.map(r=>`<tr><td>${esc(r.server)}</td><td>${esc(r.storage)}</td><td>${esc(r.applications.join(', '))}</td><td>${esc(r.before)} → ${esc(r.after)}</td><td>${esc(r.fabricBefore.join('/')||'—')} → ${esc(r.fabricAfter.join('/')||'—')}</td><td>${esc(r.pathsBefore)} → ${esc(r.pathsAfter)}</td><td>${esc(r.changedPorts.join(', '))}</td><td>${esc(r.status)}</td></tr>`).join('');return `<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Matrice d’impact SAN</title><style>body{font:14px system-ui;margin:2rem;color:#20344a}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bdc9d6;padding:.5rem;text-align:left}th{background:#eaf0f7}</style><h1>Matrice d’impact serveur → Fabric → stockage → application</h1><p>Auteur : Abdelhalim Talbi</p><p>${esc(matrix.scope)}</p><p>${matrix.summary.high} dégradation(s) ou suppression(s) ; ${matrix.summary.affectedApplications} application(s) associée(s).</p><table><thead><tr><th>Serveur</th><th>Stockage</th><th>Applications</th><th>Statut</th><th>Fabrics A/B</th><th>Chemins</th><th>Ports FC modifiés</th><th>Écart</th></tr></thead><tbody>${rows}</tbody></table></html>`;}
