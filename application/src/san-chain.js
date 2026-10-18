// OpenVisio v14.0 — chaînes SAN déclaratives. Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {auditSanPaths} from './san-audit.js';
const safe=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const text=v=>typeof v==='string'?v.trim():'';
const list=v=>Array.isArray(v)?[...new Set(v.filter(x=>typeof x==='string').map(x=>x.trim()).filter(Boolean))]:[];
export function sanChains(doc){
 validateTopology(doc);
 const nodes=new Map(doc.nodes.map(n=>[n.id,n]));
 const applications=new Map();
 for(const e of doc.edges){for(const [a,s] of [[e.from,e.to],[e.to,e.from]])if(nodes.get(a)?.type==='application'&&nodes.get(s)?.type==='server'){if(!applications.has(s))applications.set(s,new Set());applications.get(s).add(nodes.get(a).title||a);}}
 const paths=auditSanPaths(doc.nodes,doc.edges);
 return paths.map(p=>{
  const server=nodes.get(p.sourceId),storage=nodes.get(p.targetId);
  const hbas=list(server.hbas),wwpns=list(server.wwpns),luns=list(storage.luns),multipath=text(server.multipath)||'non renseigné';
  const missing=[...(!hbas.length?['HBA']:[]),...(!wwpns.length?['WWPN']:[]),...(!luns.length?['LUN']:[]),...(multipath==='non renseigné'?['multipathing']:[])];
  return {serverId:p.sourceId,server:p.sourceName,storageId:p.targetId,storage:p.targetName,fabrics:['A','B'].filter(f=>p['has'+f]),paths:p.paths,status:p.status,hbas,wwpns,luns,multipath,applications:[...(applications.get(p.sourceId)||[])].sort(),missing,quality:missing.length?'incomplete':'documented'};
 }).sort((a,b)=>a.server.localeCompare(b.server)||a.storage.localeCompare(b.storage));
}
export function compareSanChains(before,after){
 const old=new Map(sanChains(before).map(r=>[JSON.stringify([r.serverId,r.storageId]),r]));
 const now=new Map(sanChains(after).map(r=>[JSON.stringify([r.serverId,r.storageId]),r]));
 const rows=[...new Set([...old.keys(),...now.keys()])].sort().map(k=>{
  const a=old.get(k),b=now.get(k),r=b||a;
  const changes=[];for(const field of ['fabrics','hbas','wwpns','luns','multipath','applications','status','paths'])if(JSON.stringify(a?.[field]??null)!==JSON.stringify(b?.[field]??null))changes.push(field);
  return {...r,before:a||null,after:b||null,changes,change:!a?'added':!b?'removed':changes.length?'modified':'unchanged',risk:!b||((a?.fabrics.length||0)>(b?.fabrics.length||0))||((a?.paths||0)>(b?.paths||0))?'review':'none'};
 });
 return {rows,summary:{total:rows.length,changed:rows.filter(r=>r.change!=='unchanged').length,review:rows.filter(r=>r.risk==='review').length},scope:'Modèle documentaire uniquement : champs HBA/WWPN/LUN/MPIO saisis dans les propriétés des équipements, non découverts automatiquement.'};
}
export function sanChainsCsv(result){const quote=v=>{let s=String(v??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};return [['Serveur','Stockage','Fabrics','HBA','WWPN','LUN','Multipathing','Applications','Complétude','Écart','Champs modifiés','Risque'],...result.rows.map(r=>[r.server,r.storage,r.fabrics.join('/'),r.hbas.join('; '),r.wwpns.join('; '),r.luns.join('; '),r.multipath,r.applications.join('; '),r.quality,r.change,r.changes.join('; '),r.risk])].map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';}
export function sanChainsHtml(result){return `<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Chaînes SAN</title><style>body{font:14px system-ui;margin:2rem;color:#21364d}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bac6d4;padding:7px;text-align:left}th{background:#e8eff7}.review{background:#ffe3de}</style><h1>Chaînes SAN et dépendances</h1><p>Auteur : Abdelhalim Talbi</p><p>${safe(result.scope)}</p><p>${result.summary.changed} chaîne(s) modifiée(s), ${result.summary.review} à examiner.</p><table><tr><th>Serveur</th><th>Stockage</th><th>Fabric</th><th>HBA</th><th>WWPN</th><th>LUN</th><th>MPIO</th><th>Applications</th><th>Changements</th><th>Complétude</th></tr>${result.rows.map(r=>`<tr class="${r.risk==='review'?'review':''}">${[r.server,r.storage,r.fabrics.join('/'),r.hbas.join(', '),r.wwpns.join(', '),r.luns.join(', '),r.multipath,r.applications.join(', '),r.changes.join(', '),r.missing.join(', ')||'documenté'].map(v=>`<td>${safe(v)}</td>`).join('')}</tr>`).join('')}</table></html>`;}
