import {validateSanHistory} from './san-cockpit.js';
import {compareSanImports} from './zoneset-document.js';
export function compareFabricSnapshots(history,{maxAgeDays=30,requireBothFabrics=true}={}){
 const entries=validateSanHistory(history);const latest={};for(const e of entries)latest[e.data.fabric]=e;
 const issues=[];const now=Date.now();
 for(const fabric of ['A','B']){
  const e=latest[fabric];if(!e){if(requireBothFabrics)issues.push({severity:'warning',code:'FABRIC_MISSING',fabric,detail:`Aucun import Fabric ${fabric}`});continue;}
  if(maxAgeDays>0 && now-Date.parse(e.at)>maxAgeDays*86400000)issues.push({severity:'warning',code:'SNAPSHOT_STALE',fabric,detail:`Import Fabric ${fabric} ancien`});
  const names=new Set(e.data.zones.map(z=>z.name));for(const set of e.data.zonesets)for(const name of set.zones)if(!names.has(name))issues.push({severity:'error',code:'ZONE_UNDEFINED',fabric,detail:`${set.name}: ${name}`});
 }
 const a=latest.A?.data,b=latest.B?.data;
 const zonesByFabric={A:a?.zones.length??0,B:b?.zones.length??0};
 const setsByFabric={A:a?.zonesets.length??0,B:b?.zonesets.length??0};
 const score=entries.length?Math.max(0,100-issues.filter(x=>x.severity==='error').length*20-issues.filter(x=>x.severity==='warning').length*10):0;
 return {latest,issues,score,zonesByFabric,setsByFabric,comparison:a&&b?compareSanImports(a,b):[],rules:{maxAgeDays,requireBothFabrics}};
}
export function complianceCsv(result){const esc=v=>'"'+String(v??'').replaceAll('"','""').replace(/^[=+@\-]/,"'$&")+'"';return '\uFEFF'+[['Type','Fabric','Code','Détail'],...result.issues.map(i=>['Alerte',i.fabric,i.code,i.detail]),...result.comparison.map(i=>['Comparaison','A/B',i.status,i.key])].map(row=>row.map(esc).join(';')).join('\r\n');}
