// OpenVisio v30.3 — comparaison documentaire des pannes Fabric A/B. Auteur : Abdelhalim Talbi.
const count=n=>Number.isFinite(Number(n))?Math.max(0,Math.trunc(Number(n))):0;
export function compareFabricFailures(row){
 const a=count(row?.fabricA),b=count(row?.fabricB);
 const common=[...new Set((row?.sharedTransitIds||[]).filter(x=>typeof x==='string'&&x.trim()))].sort();
 const baseline=a+b;
 const cases=[{id:'NORMAL',remainingA:a,remainingB:b},{id:'FABRIC_A_DOWN',remainingA:0,remainingB:b},{id:'FABRIC_B_DOWN',remainingA:a,remainingB:0}].map(s=>({ ...s, remainingPaths:s.remainingA+s.remainingB, lostPaths:baseline-s.remainingA-s.remainingB, status:s.remainingA+s.remainingB===0?'LOSS':s.remainingA===0||s.remainingB===0?'DEGRADED':'DOCUMENTED_DUAL_FABRIC' }));
 return {serverId:String(row?.serverId??''),storageId:String(row?.storageId??''),sharedTransitIds:common,baselinePaths:baseline,cases,warning:common.length?'Dépendances communes documentées : indépendance à vérifier.':'La topologie seule ne prouve pas le multipathing réel.'};
}
export function scenarioFocusIds(row){return [...new Set([row?.serverId,row?.storageId,...(row?.sharedTransitIds||[])].filter(x=>typeof x==='string'&&x.trim()))];}
export function formatFabricComparison(result){return result.cases.map(s=>`${s.id}: ${s.remainingPaths}/${result.baselinePaths} chemins documentés (${s.status})`).join(' · ')+` · ${result.warning}`;}

// v30.4 — comparative report, explicit distinction between documented paths and real availability.
export function buildFailureComparisonReport(matrix){
 const rows=(matrix?.rows||[]).map(row=>({priority:row.priority,serverId:String(row.serverId??''),storageId:String(row.storageId??''),...compareFabricFailures(row)}));
 return {rows,truncated:Boolean(matrix?.truncated),disclaimer:'Simulation documentaire : ne valide ni zoning, ni masking, ni multipathing effectif.'};
}
export function failureComparisonCsv(report){
 const safe=value=>{let s=String(value??'');if(/^\s*[=+@-]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';};
 const data=[['priority','server','storage','scenario','baseline','remaining','lost','status','shared_transit','warning']];
 for(const row of report?.rows||[])for(const c of row.cases)data.push([row.priority,row.serverId,row.storageId,c.id,row.baselinePaths,c.remainingPaths,c.lostPaths,c.status,row.sharedTransitIds.join(';'),row.warning]);
 return data.map(line=>line.map(safe).join(',')).join('\r\n')+'\r\n';
}
