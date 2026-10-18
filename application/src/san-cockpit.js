import {validateSanImport,compareSanImports} from './zoneset-document.js';
export function appendSanSnapshot(history,importData,{label='',at=new Date().toISOString()}={}){
 const snapshot=validateSanImport(importData);if(!snapshot)throw Error('Import SAN requis');
 const existing=validateSanHistory(history);
 const entry={id:`${at}:${existing.length}`,at,label:String(label).slice(0,100),data:snapshot};
 return [...existing,entry].slice(-30);
}
export function validateSanHistory(history){
 if(!Array.isArray(history)||history.length>30)throw Error('Historique SAN invalide');
 return history.map((entry,i)=>{
  if(!entry||typeof entry!=='object'||typeof entry.at!=='string'||!Number.isFinite(Date.parse(entry.at)))throw Error('Date historique invalide');
  return {id:String(entry.id??i).slice(0,100),at:entry.at,label:String(entry.label??'').slice(0,100),data:validateSanImport(entry.data)};
 });
}
export function cockpitSummary(history,declaredZones=[]){
 const entries=validateSanHistory(history);
 const fabrics={A:0,B:0};const alerts=[];
 for(const entry of entries){fabrics[entry.data.fabric]++;const zoneNames=new Set(entry.data.zones.map(z=>z.name));
  for(const set of entry.data.zonesets){for(const zone of set.zones)if(!zoneNames.has(zone))alerts.push({at:entry.at,fabric:entry.data.fabric,code:'MISSING_ZONE',detail:`${set.name}: ${zone}`});}
 }
 const last=entries.at(-1),prior=entries.at(-2);
 const changes=prior&&last?compareSanImports(prior.data,last.data):[];
 return {snapshots:entries.length,fabrics,alerts,changes,changed:changes.filter(x=>x.status!=='unchanged').length,declaredZones:declaredZones.length};
}
export function cockpitCsv(summary){const esc=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[=+@\-]/,"'$&")+'"';return '\uFEFF'+[['Type','Fabric / zoneset','Statut','Détail'],...summary.changes.map(c=>['Diff',c.key,c.status,c.after]),...summary.alerts.map(a=>['Alerte',a.fabric,a.code,a.detail])].map(r=>r.map(esc).join(';')).join('\r\n');}
