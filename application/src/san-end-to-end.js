// OpenVisio v14.6 — validation consolidée déclarative. Auteur : Abdelhalim Talbi.
import {auditSanAccess} from './san-access-audit.js';
import {auditSanPaths} from './san-audit.js';
const clean=x=>String(x??'').trim();
const esc=x=>clean(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csv=x=>{let v=clean(x);if(/^\s*[=+@-]/.test(v))v="'"+v;return '"'+v.replaceAll('"','""')+'"';};
export function validateSanEndToEnd(doc,imported=null){
 const access=auditSanAccess(doc,imported);
 const paths=auditSanPaths(doc.nodes,doc.edges);
 const byId=new Map(doc.nodes.map(n=>[n.id,n]));
 const grouped=new Map();
 for(const edge of doc.edges){const a=byId.get(edge.from),b=byId.get(edge.to);if(!a||!b)continue;
  const server=a.type==='server'?a:b.type==='server'?b:null;
  const storage=a.type==='storage'?a:b.type==='storage'?b:null;
  if(!server||!storage)continue;
  const lun=clean(edge.lunId);const key=JSON.stringify([server.id,storage.id,lun]);
  if(!grouped.has(key))grouped.set(key,{serverId:server.id,storageId:storage.id,server:clean(server.title)||server.id,storage:clean(storage.title)||storage.id,lun,edges:[],fabrics:new Set(),issues:new Set()});
  const g=grouped.get(key);g.edges.push(edge.id);if(['A','B'].includes(clean(edge.fabric).toUpperCase()))g.fabrics.add(clean(edge.fabric).toUpperCase());
  const accessRow=access.rows.find(r=>r.edgeId===edge.id);for(const issue of accessRow?.issues||[])g.issues.add(issue);
 }
 const rows=[...grouped.values()].map(g=>{
  if(!g.lun)g.issues.add('LUN_MISSING');
  if(g.fabrics.size<2)g.issues.add('FABRIC_REDUNDANCY_NOT_DEMONSTRATED');
  const related=paths.filter(p=>p.sourceId===g.serverId&&p.targetId===g.storageId);
  if(related.some(p=>p.spof?.length))g.issues.add('PATH_SINGLE_POINT_OF_FAILURE');
  const issues=[...g.issues].sort();return {server:g.server,storage:g.storage,lun:g.lun,edges:g.edges,fabrics:[...g.fabrics].sort(),issues,severity:issues.some(i=>/SINGLE_POINT|REDUNDANCY|MASKING_PAIR|ZONING_/.test(i))?'high':issues.length?'medium':'documented'};
 }).sort((a,b)=>a.server.localeCompare(b.server)||a.storage.localeCompare(b.storage)||a.lun.localeCompare(b.lun));
 return {rows,summary:{total:rows.length,high:rows.filter(r=>r.severity==='high').length,medium:rows.filter(r=>r.severity==='medium').length,documented:rows.filter(r=>r.severity==='documented').length},scope:'Contrôle documentaire uniquement : les chemins, zoning, masking et multipathing sont déclarés dans les diagrammes et imports, sans interrogation du matériel.'};
}
export function sanEndToEndCsv(result){return [['Serveur','Stockage','LUN','Fabrics','Connexions','Criticité','Anomalies'],...result.rows.map(r=>[r.server,r.storage,r.lun,r.fabrics.join('/'),r.edges.join('; '),r.severity,r.issues.join('; ')])].map(r=>r.map(csv).join(',')).join('\r\n')+'\r\n';}
export function sanEndToEndHtml(result){return '<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Validation SAN de bout en bout</title><style>body{font:14px system-ui;margin:2rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:7px}.high{background:#ffe0dc}.medium{background:#fff1d6}</style><h1>Validation SAN de bout en bout</h1><p>Auteur : Abdelhalim Talbi</p><p>'+esc(result.scope)+'</p><p>'+result.summary.high+' criticité(s) haute(s), '+result.summary.medium+' moyenne(s) sur '+result.summary.total+' chaîne(s).</p><table><tr>'+['Serveur','Stockage','LUN','Fabrics','Criticité','Anomalies'].map(esc).map(v=>'<th>'+v+'</th>').join('')+'</tr>'+result.rows.map(r=>'<tr class="'+r.severity+'">'+[r.server,r.storage,r.lun,r.fabrics.join('/'),r.severity,r.issues.join(', ')].map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</table></html>';}
