// OpenVisio v14.7 — simulation non destructive de panne SAN. Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {auditSanPaths} from './san-audit.js';
import {applicationImpact} from './san-port-impact.js';
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csv=x=>{let s=String(x??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
export function failureTargets(doc){validateTopology(doc);const fabrics=[...new Set(doc.edges.map(e=>String(e.fabric||'').toUpperCase()).filter(x=>x==='A'||x==='B'))].sort();return [...fabrics.map(id=>({kind:'fabric',id,label:'Fabric '+id})),...doc.nodes.map(n=>({kind:'node',id:n.id,label:n.title||n.id})),...doc.edges.map(e=>({kind:'edge',id:e.id,label:e.id}))];}
export function simulateSanFailure(doc,{kind,id}){
 validateTopology(doc);if(!['fabric','node','edge'].includes(kind)||typeof id!=='string')throw new Error('Cible de panne invalide');
 const targets=failureTargets(doc);if(!targets.some(t=>t.kind===kind&&t.id===id))throw new Error('Cible absente du diagramme');
 const nodes=kind==='node'?doc.nodes.filter(n=>n.id!==id):doc.nodes.slice();
 const edges=doc.edges.filter(e=>kind==='node'?(e.from!==id&&e.to!==id):kind==='edge'?e.id!==id:String(e.fabric||'').toUpperCase()!==id);
 const scenario={...doc,nodes,edges};
 const before=auditSanPaths(doc.nodes,doc.edges),after=auditSanPaths(nodes,edges);
 const index=new Map(after.map(r=>[JSON.stringify([r.sourceId,r.targetId]),r]));
 const severity={redundant:2,'at-risk':1,unreachable:0};
 const rows=before.map(b=>{const a=index.get(JSON.stringify([b.sourceId,b.targetId]));const status=a?.status||'unreachable';const degraded=(severity[status]??0)<(severity[b.status]??0);return {server:b.sourceName,storage:b.targetName,serverId:b.sourceId,storageId:b.targetId,before:b.status,after:status,pathsBefore:b.paths,pathsAfter:a?.paths||0,impact:degraded?(status==='unreachable'?'loss':'degraded'):'unchanged'};});
 const impacted=rows.filter(r=>r.impact!=='unchanged');
 // Application relationships are derived from explicit diagram connections only.
 const appRows=applicationImpact(doc,scenario).filter(r=>r.impactedPairs>0);
 return {target:{kind,id},rows,applications:appRows,summary:{pairs:rows.length,affected:impacted.length,loss:impacted.filter(r=>r.impact==='loss').length,applications:appRows.length},scope:'Simulation documentaire sans action sur les équipements ; chemins déduits du diagramme, sans garantie de connectivité réelle.'};
}
export function failureCsv(r){return [['Serveur','Stockage','Avant','Après','Chemins avant','Chemins après','Impact'],...r.rows.map(x=>[x.server,x.storage,x.before,x.after,x.pathsBefore,x.pathsAfter,x.impact])].map(a=>a.map(csv).join(',')).join('\r\n')+'\r\n';}
export function failureHtml(r){return '<!doctype html><html lang="fr"><meta charset="utf-8"><title>Simulation SAN OpenVisio</title><style>body{font:14px system-ui;margin:2rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:7px}.loss{background:#ffd9d9}.degraded{background:#fff0cc}</style><h1>Simulation de panne SAN</h1><p>Auteur : Abdelhalim Talbi</p><p>'+esc(r.scope)+'</p><p>Cible : '+esc(r.target.kind)+' / '+esc(r.target.id)+' — '+r.summary.affected+' paire(s) affectée(s).</p><table><tr>'+['Serveur','Stockage','Avant','Après','Chemins','Impact'].map(x=>'<th>'+x+'</th>').join('')+'</tr>'+r.rows.map(x=>'<tr class="'+esc(x.impact)+'">'+[x.server,x.storage,x.before,x.after,x.pathsBefore+' → '+x.pathsAfter,x.impact].map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('')+'</table><h2>Applications associées</h2><ul>'+r.applications.map(x=>'<li>'+esc(x.applicationName)+' — '+esc(x.impactedPairs)+' paire(s) affectée(s)</li>').join('')+'</ul></html>';}

// v14.8 — scénarios combinés, déduplication et classement de résilience.
export function simulateMultipleSanFailures(doc, failures){
 validateTopology(doc);
 if(!Array.isArray(failures)||failures.length===0||failures.length>50)throw new Error('Sélectionnez entre 1 et 50 défaillances');
 const known=new Set(failureTargets(doc).map(t=>JSON.stringify([t.kind,t.id])));
 const selected=[];const seen=new Set();
 for(const f of failures){const key=JSON.stringify([f?.kind,f?.id]);if(!known.has(key))throw new Error('Cible de panne absente : '+String(f?.id));if(!seen.has(key)){selected.push({kind:f.kind,id:f.id});seen.add(key);}}
 const failedNodes=new Set(selected.filter(f=>f.kind==='node').map(f=>f.id));
 const failedEdges=new Set(selected.filter(f=>f.kind==='edge').map(f=>f.id));
 const failedFabrics=new Set(selected.filter(f=>f.kind==='fabric').map(f=>f.id));
 const nodes=doc.nodes.filter(n=>!failedNodes.has(n.id));
 const edges=doc.edges.filter(e=>!failedEdges.has(e.id)&&!failedNodes.has(e.from)&&!failedNodes.has(e.to)&&!failedFabrics.has(String(e.fabric||'').toUpperCase()));
 const scenario={...doc,nodes,edges};
 const before=auditSanPaths(doc.nodes,doc.edges),after=auditSanPaths(nodes,edges);
 const index=new Map(after.map(r=>[JSON.stringify([r.sourceId,r.targetId]),r]));
 const rank={redundant:2,'at-risk':1,unreachable:0};
 const rows=before.map(b=>{const a=index.get(JSON.stringify([b.sourceId,b.targetId]));const status=a?.status||'unreachable';const impact=(rank[status]??0)<(rank[b.status]??0)?(status==='unreachable'?'loss':'degraded'):'unchanged';return {server:b.sourceName,storage:b.targetName,serverId:b.sourceId,storageId:b.targetId,before:b.status,after:status,pathsBefore:b.paths,pathsAfter:a?.paths||0,impact};});
 const apps=applicationImpact(doc,scenario).filter(a=>a.impactedPairs>0);
 const affected=rows.filter(r=>r.impact!=='unchanged');
 return {targets:selected,rows,applications:apps,summary:{pairs:rows.length,affected:affected.length,loss:affected.filter(r=>r.impact==='loss').length,degraded:affected.filter(r=>r.impact==='degraded').length,applications:apps.length},scope:'Simulation documentaire combinée ; aucun équipement réel modifié. Les chemins et impacts proviennent du diagramme.'};
}
export function multipleFailureCsv(result){return [['Type','Identifiant'],...result.targets.map(t=>[t.kind,t.id])].map(r=>r.map(csv).join(',')).join('\r\n')+'\r\n'+failureCsv(result);}
export function multipleFailureHtml(result){const targetList=result.targets.map(t=>'<li>'+esc(t.kind)+' : '+esc(t.id)+'</li>').join('');return failureHtml({...result,target:{kind:'scénario combiné',id:result.targets.length+' défaillance(s)'}}).replace('<h2>Applications associées</h2>','<h2>Défaillances simulées</h2><ul>'+targetList+'</ul><h2>Applications associées</h2>');}
