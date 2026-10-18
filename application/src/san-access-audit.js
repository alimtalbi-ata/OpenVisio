// OpenVisio v14.4 — audit documentaire zoning / masking / multipathing.
// Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {correlateSanZoning} from './san-zoning-correlation.js';
const clean=v=>String(v??'').trim();
const norm=v=>clean(v).toLowerCase();
const escape=v=>clean(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csv=v=>{let s=String(v??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
const asList=v=>Array.isArray(v)?v.map(clean).filter(Boolean):[];
export function auditSanAccess(doc,imported=null){
 validateTopology(doc);
 const nodes=new Map(doc.nodes.map(n=>[n.id,n]));
 const zoning=imported?correlateSanZoning(doc,imported):null;
 const zoneRows=new Map((zoning?.rows||[]).map(r=>[r.edgeId,r]));
 const rows=[];
 for(const edge of doc.edges){
  const hasSan= ['initiatorWwpn','targetWwpn','zoneName','lunId','pathId'].some(k=>clean(edge[k]));
  if(!hasSan)continue;
  const source=nodes.get(edge.from),target=nodes.get(edge.to);
  const issues=[];const lun=clean(edge.lunId),initiator=clean(edge.initiatorWwpn),path=clean(edge.pathId);
  if(!initiator)issues.push('INITIATOR_MISSING');
  if(!clean(edge.targetWwpn))issues.push('TARGET_WWPN_MISSING');
  if(!lun)issues.push('LUN_MISSING');
  if(!path)issues.push('PATH_ID_MISSING');
  if(lun&&target&& !asList(target.luns).some(x=>norm(x)===norm(lun)))issues.push('LUN_NOT_DECLARED_ON_TARGET');
  if(initiator&&source&& !asList(source.wwpns).some(x=>norm(x)===norm(initiator)))issues.push('INITIATOR_NOT_DECLARED_ON_SOURCE');
  // Le masking doit être explicite : une LUN visible dans l'inventaire ne suffit pas.
  const masks=Array.isArray(target?.lunMasking)?target.lunMasking:[];
  if(!masks.length)issues.push('MASKING_NOT_DOCUMENTED');
  else if(lun&&initiator&&!masks.some(m=>m&&norm(m.lunId)===norm(lun)&&norm(m.initiatorWwpn)===norm(initiator)))issues.push('MASKING_PAIR_NOT_DECLARED');
  const mp=norm(source?.multipath);
  if(!mp)issues.push('MULTIPATH_NOT_DOCUMENTED');
  const z=zoneRows.get(edge.id);
  if(!z)issues.push(imported?'ZONING_LINK_NOT_AUDITED':'ZONING_IMPORT_UNAVAILABLE');
  else issues.push(...z.issues.map(i=>'ZONING_'+i));
  rows.push({edgeId:edge.id,source:source?.title||edge.from,target:target?.title||edge.to,lun,initiator,path,fabric:clean(edge.fabric)||'',multipath:clean(source?.multipath),issues:[...new Set(issues)],status:issues.length?'review':'documented'});
 }
 const groups=new Map();
 for(const r of rows){const key=JSON.stringify([r.source,r.target,r.lun]);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(r);}
 for(const group of groups.values()){
  const ids=group.map(r=>norm(r.path)).filter(Boolean);
  if(ids.length!==new Set(ids).size)for(const r of group)r.issues.push('DUPLICATE_PATH_ID');
  const fabrics=new Set(group.map(r=>norm(r.fabric)).filter(Boolean));
  if(group.length>1&&fabrics.size<2)for(const r of group)r.issues.push('FABRIC_REDUNDANCY_NOT_DEMONSTRATED');
 }
 for(const r of rows)r.status=r.issues.length?'review':'documented';
 return {rows,summary:{total:rows.length,review:rows.filter(r=>r.issues.length).length,documented:rows.filter(r=>!r.issues.length).length},scope:'Audit déclaratif. Les entrées lunMasking du stockage sont des déclarations documentaires, pas une lecture du masking réel. Multipathing et disponibilité effective non vérifiés.'};
}
export function sanAccessCsv(report){return [['Lien','Source','Cible','LUN','WWPN initiateur','Chemin','Fabric','Multipathing','Statut','Anomalies'],...report.rows.map(r=>[r.edgeId,r.source,r.target,r.lun,r.initiator,r.path,r.fabric,r.multipath,r.status,r.issues.join('; ')])].map(row=>row.map(csv).join(',')).join('\r\n')+'\r\n';}
export function sanAccessHtml(report){return '<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Accès SAN</title><style>body{font:14px system-ui;margin:2rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #abb;padding:7px}.review{background:#ffe4de}</style><h1>Audit zoning / masking / multipathing</h1><p>Auteur : Abdelhalim Talbi</p><p>'+escape(report.scope)+'</p><p>'+report.summary.review+' à examiner sur '+report.summary.total+'</p><table><tr>'+['Source','Cible','LUN','WWPN initiateur','Chemin','Fabric','Multipathing','Anomalies'].map(x=>'<th>'+escape(x)+'</th>').join('')+'</tr>'+report.rows.map(r=>'<tr class="'+(r.issues.length?'review':'')+'">'+[r.source,r.target,r.lun,r.initiator,r.path,r.fabric,r.multipath,r.issues.join(', ')].map(v=>'<td>'+escape(v)+'</td>').join('')+'</tr>').join('')+'</table></html>';}
