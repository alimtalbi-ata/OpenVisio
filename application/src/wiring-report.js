import {auditZoning} from './zoning.js';
import {auditSanPaths,zoningReview} from './san-audit.js';
// Auteur : Abdelhalim Talbi — rapports de câblage v12.0.
import {portInventory,cableDiagnostics,fabricDiagnostics,fabricRedundancy} from './ports.js';
export function buildWiringReport(nodes,edges,zones=[]){
 const zoning=auditZoning(nodes,edges,zones);
 const inventory=portInventory(nodes,edges);
 const diagnostics=[...cableDiagnostics(nodes,edges),...fabricDiagnostics(nodes,edges),...zoningReview(nodes,edges)];
 const redundancy=fabricRedundancy(nodes,edges);
 const matrix=redundancy.map(row=>({...row,hasA:row.fabrics.includes('A'),hasB:row.fabrics.includes('B')}));
 const counts={free:0,used:0,conflict:0};for(const item of inventory)counts[item.status]++;
 const sanPaths=auditSanPaths(nodes,edges);
 return {inventory,diagnostics,matrix,sanPaths,zoning,counts,generatedAt:new Date().toISOString()};
}
export function csvEscape(value){const s=String(value??'');return /[",\r\n;]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;}
export function toCsv(rows,columns){const head=columns.map(c=>csvEscape(c[0])).join(';');return '\uFEFF'+[head,...rows.map(row=>columns.map(([,key])=>csvEscape(row[key])).join(';'))].join('\r\n')+'\r\n';}
export function reportCsv(report,kind){
 if(kind==='ports')return toCsv(report.inventory.map(p=>({...p,edgeIds:p.edgeIds.join('|'),findings:p.findings.map(f=>f.code).join('|')})),[['Equipement','nodeTitle'],['Port','port'],['Famille','family'],['Etat','status'],['Connexions','edgeIds'],['Anomalies','findings']]);
 if(kind==='fabric')return toCsv(report.matrix.map(r=>({...r,fabricA:r.hasA?'Oui':'Non',fabricB:r.hasB?'Oui':'Non',redundant:r.redundant?'Oui':'Non'})),[['Equipement','nodeTitle'],['Fabric A','fabricA'],['Fabric B','fabricB'],['Double chemin','redundant']]);
 if(kind==='san-paths')return toCsv(report.sanPaths.map(r=>({...r,spof:r.spof.join('|')})),[['Serveur','sourceName'],['Stockage','targetName'],['Fabric A','hasA'],['Fabric B','hasB'],['Chemins independants','independent'],['Nombre de chemins','paths'],['SPOF','spof'],['Etat','status']]);
 if(kind==='zoning')return toCsv(report.zoning.matrix,[['Zone','zone'],['Fabric','fabric'],['Initiateur WWPN','initiator'],['Cible WWPN','target']]);
 if(kind==='anomalies')return toCsv(report.diagnostics.map(x=>({...x,port:x.port||'',side:x.side||''})),[['Connexion','edgeId'],['Code','code'],['Port','port'],['Cote','side']]);
 throw Error('Rapport inconnu');
}

// v12.2 : rapport autonome, échappement systématique des champs non fiables.
export function escapeHtml(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
export function reportHtml(report){
 const table=(headers,rows)=>'<table><thead><tr>'+headers.map(x=>'<th>'+escapeHtml(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(x=>'<td>'+escapeHtml(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
 const paths=report.sanPaths||[], diagnostics=report.diagnostics||[];
 const statuses={redundant:0,'at-risk':0,unreachable:0};for(const p of paths)if(p.status in statuses)statuses[p.status]++;
 return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Audit SAN OpenVisio</title><style>body{font:14px system-ui;margin:2rem;color:#17243b}h1{color:#17447b}table{border-collapse:collapse;width:100%;margin:1rem 0 2rem}th,td{border:1px solid #cbd5e1;padding:.5rem;text-align:left}th{background:#eaf2ff}small{color:#475569}@media print{body{margin:12mm}table{break-inside:auto}tr{break-inside:avoid}}</style></head><body><h1>OpenVisio — Audit SAN</h1><p>Rapport généré : '+escapeHtml(report.generatedAt)+' · '+paths.length+' couples serveur/stockage · '+statuses.redundant+' redondants · '+statuses['at-risk']+' à risque · '+statuses.unreachable+' inaccessibles</p><h2>Chemins et points uniques de défaillance</h2>'+table(['Serveur','Stockage','Fabric A','Fabric B','Indépendants','SPOF','État'],paths.map(p=>[p.sourceName,p.targetName,p.hasA?'Oui':'Non',p.hasB?'Oui':'Non',p.independent?'Oui':'Non',(p.spof||[]).join(', ')||'—',p.status]))+'<h2>Zoning déclaré</h2>'+table(['Zone','Fabric','Initiateur WWPN','Cible WWPN'],(report.zoning?.matrix||[]).map(x=>[x.zone,x.fabric,x.initiator,x.target]))+'<h2>Alertes de zoning</h2>'+table(['Code','Zone','Détail'],(report.zoning?.findings||[]).map(x=>[x.code,x.zone||'',x.value||x.initiator||'']))+'<h2>Zonesets importés (déclaratif)</h2>'+table(['Fabric','VSAN','Zoneset','Zone','Activation commandée','Comparaison'],(report.zonesetAudit?.rows||[]).map(x=>[x.fabric,x.vsan??'—',x.zoneset,x.zone,x.activationDeclared?'Oui':'Non',x.status]))+'<h2>Anomalies déclaratives</h2>'+table(['Connexion','Code','Port'],diagnostics.map(x=>[x.edgeId,x.code,x.port||'—']))+'<small>Analyse topologique déclarative uniquement. Le zoning est déclaratif ; sa configuration effective, les chemins actifs, les ACL et la résilience réelle ne sont pas vérifiés. Auteur : Abdelhalim Talbi.</small></body></html>';
}

export function zonesetAuditCsv(audit){return toCsv(audit.rows||[],[['Fabric','fabric'],['VSAN','vsan'],['Zoneset','zoneset'],['Zone','zone'],['Activation commandée','activationDeclared'],['Comparaison','status']]);}
