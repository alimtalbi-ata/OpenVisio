// OpenVisio v14.3 — rapprochement déclaratif zoning / liens SAN. Auteur : Abdelhalim Talbi.
import {validateTopology} from './topology-diff.js';
import {validateSanImport} from './zoneset-document.js';
const norm=v=>String(v??'').trim().toLowerCase();
const html=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const csv=v=>{let s=String(v??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
export function correlateSanZoning(doc,imported){
 validateTopology(doc);
 const config=validateSanImport(imported);
 if(!config)throw Error('Import SAN absent');
 const nodes=new Map(doc.nodes.map(n=>[n.id,n]));
 const zoneMap=new Map();
 for(const zone of config.zones||[]){const key=norm(zone.name);if(!zoneMap.has(key))zoneMap.set(key,[]);zoneMap.get(key).push(zone);}
 const active=new Set((config.activeConfigurations||[]).map(c=>`${norm(c.vsan??'')}:${norm(c.name)}`));
 const referenced=new Set();const activeZones=new Set();
 for(const set of config.zonesets||[]){for(const name of set.zones||[]){const k=`${norm(set.vsan??'')}:${norm(name)}`;referenced.add(k);if(active.has(`${norm(set.vsan??'')}:${norm(set.name)}`))activeZones.add(k);}}
 const rows=[];
 for(const edge of doc.edges){const issues=[];const zoneName=norm(edge.zoneName);const initiator=norm(edge.initiatorWwpn);const target=norm(edge.targetWwpn);const vsan=norm(edge.vsan??'');
 if(!zoneName&&!initiator&&!target)continue;
 if(!zoneName)issues.push('ZONE_NOT_SPECIFIED');
 const candidates=zoneMap.get(zoneName)||[];
 const matches=candidates.filter(z=>vsan===''||norm(z.vsan??'')===vsan);
 if(zoneName&&!matches.length)issues.push('ZONE_NOT_IN_IMPORT');
 if(zoneName&&matches.length&&vsan===''&&new Set(matches.map(z=>norm(z.vsan??''))).size>1)issues.push('AMBIGUOUS_VSAN');
 if(!initiator)issues.push('INITIATOR_MISSING');if(!target)issues.push('TARGET_MISSING');
 if(matches.length){const memberSets=matches.map(z=>new Set([...(z.members||[]),...(z.initiators||[]),...(z.targets||[])].map(norm)));
 if(initiator&&!memberSets.some(m=>m.has(initiator)))issues.push('INITIATOR_NOT_IN_ZONE');
 if(target&&!memberSets.some(m=>m.has(target)))issues.push('TARGET_NOT_IN_ZONE');
 if(!matches.some(z=>referenced.has(`${norm(z.vsan??'')}:${zoneName}`)))issues.push('ZONE_NOT_IN_ZONESET');
 if(!matches.some(z=>activeZones.has(`${norm(z.vsan??'')}:${zoneName}`)))issues.push('NO_DECLARED_ACTIVATION');
 }
 rows.push({edgeId:edge.id,source:nodes.get(edge.from)?.title||edge.from,target:nodes.get(edge.to)?.title||edge.to,zone:edge.zoneName||'',initiator:edge.initiatorWwpn||'',targetWwpn:edge.targetWwpn||'',vsan:edge.vsan??'',issues,status:issues.length?'review':'matched'});
 }
 return {rows,summary:{total:rows.length,review:rows.filter(r=>r.issues.length).length,matched:rows.filter(r=>!r.issues.length).length},scope:'Rapprochement déclaratif entre un diagramme et un import SAN. Une activation déclarée ne prouve pas le zoning actif, le masking LUN ni la connectivité effective.'};
}
export function zoningCorrelationCsv(report){return [['Lien','Source','Cible','Zone','VSAN','WWPN initiateur','WWPN cible','État','Anomalies'],...report.rows.map(r=>[r.edgeId,r.source,r.target,r.zone,r.vsan,r.initiator,r.targetWwpn,r.status,r.issues.join('; ')])].map(r=>r.map(csv).join(',')).join('\r\n')+'\r\n';}
export function zoningCorrelationHtml(report){return '<!doctype html><html lang="fr"><meta charset="utf-8"><title>OpenVisio — Corrélation zoning</title><style>body{font:14px system-ui;margin:2rem}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aab;padding:7px}.review{background:#ffe4de}</style><h1>Corrélation zoning / connexions</h1><p>Auteur : Abdelhalim Talbi</p><p>'+html(report.scope)+'</p><p>'+report.summary.review+' à examiner sur '+report.summary.total+'</p><table><tr>'+['Lien','Source','Cible','Zone','VSAN','WWPN initiateur','WWPN cible','Anomalies'].map(x=>'<th>'+html(x)+'</th>').join('')+'</tr>'+report.rows.map(r=>'<tr class="'+(r.issues.length?'review':'')+'">'+[r.edgeId,r.source,r.target,r.zone,r.vsan,r.initiator,r.targetWwpn,r.issues.join(', ')].map(x=>'<td>'+html(x)+'</td>').join('')+'</tr>').join('')+'</table></html>';}
