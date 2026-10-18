// OpenVisio v31.3 — corrélation non destructive de preuves SAN. Auteur : Abdelhalim Talbi.
import {normalizeWwpn} from './san-config-import-v311.js';
import {traceSanPaths} from './san-path-trace-v307.js';
const safe=x=>String(x??'').trim();
const unique=a=>[...new Set(a)];
export function correlateSanImport(snapshot, imported){
 const trace=traceSanPaths(snapshot);
 const zones=Array.isArray(imported?.zones)?imported.zones:[];
 const findings=[];
 for(const [index,path] of trace.paths.entries()){
  const ids=unique(path.hops.map(h=>safe(h.edgeId)).filter(Boolean));
  const endpoints=path.hops.filter(h=>normalizeWwpn(h.sourceWwpn)||normalizeWwpn(h.targetWwpn));
  const initiator=normalizeWwpn(endpoints[0]?.sourceWwpn);
  const target=normalizeWwpn(endpoints.at(-1)?.targetWwpn);
  const resolved=resolveZoneAliases(imported);
  const matching=initiator&&target?resolved.filter(z=>z.members.includes(initiator)&&z.members.includes(target)):[];
  const status=!initiator||!target?'UNKNOWN_WWPN':!zones.length?'NO_ZONE_EVIDENCE':matching.length?'DOCUMENTED_PAIR':'PAIR_NOT_IN_IMPORT';
  findings.push({path:index+1,serverId:path.serverId,storageId:path.storageId,edgeIds:ids,initiatorWwpn:initiator,targetWwpn:target,status,zoneNames:matching.map(z=>safe(z.name)),evidenceConfidence:matching.some(z=>z.configurationState==='active')?'ACTIVE_DECLARED':matching.length?'CONFIGURED_OR_UNKNOWN':'NONE',zoneEvidence:matching.map(z=>({name:z.name,configurationState:z.configurationState,vsan:z.vsan})),severity:status==='DOCUMENTED_PAIR'?'INFO':'REVIEW',reason:status==='PAIR_NOT_IN_IMPORT'?'Paire absente de cet extrait; vérifier que l’export couvre le zoning actif.':status==='UNKNOWN_WWPN'?'WWPN d’extrémité non renseigné dans le diagramme.':status==='NO_ZONE_EVIDENCE'?'Aucune zone exploitable dans cet import.':'Paire documentée dans une zone importée.'});
 }
 return {findings,truncated:trace.truncated,limitations:['Export partiel : absence de preuve ≠ absence de zoning','Aucun état réel de switch, masking ou multipathing attesté']};
}
export function sanCorrelationCsv(report){const cell=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[\s]*[=+@\-]/,"'$&")+'"';return [['path','server','storage','status','initiator_wwpn','target_wwpn','zones','connections','evidence_confidence','recommendation'],...(report?.findings??[]).map(f=>[f.path,f.serverId,f.storageId,f.status,f.initiatorWwpn,f.targetWwpn,f.zoneNames.join(';'),f.edgeIds.join(';'),f.evidenceConfidence,evidenceRecommendation(f)])].map(r=>r.map(cell).join(',')).join('\r\n');}

// v31.4: only explicit alias definitions are expanded; active zoning is never inferred.
export function resolveZoneAliases(imported){
 const aliases=Array.isArray(imported?.aliases)?imported.aliases:[];
 const map=new Map(aliases.map(a=>[safe(a.name).toLowerCase(),a]));
 const resolve=(member,seen=new Set())=>{const w=normalizeWwpn(member);if(w)return [w];const name=safe(member).toLowerCase();if(!name||seen.has(name))return [];const alias=map.get(name);if(!alias)return [];const next=new Set(seen);next.add(name);return (alias.members??[]).flatMap(m=>resolve(m,next));};
 return (Array.isArray(imported?.zones)?imported.zones:[]).map(z=>({ ...z, members:unique((z.members??[]).flatMap(m=>resolve(m))), configurationState:['active','configured'].includes(z.configurationState)?z.configurationState:'unknown' }));
}

// v31.6: recommendations are documentary; missing evidence never implies an outage.
export function evidenceRecommendation(f){
 if(f?.evidenceConfidence==='ACTIVE_DECLARED')return 'Vérifier la concordance des WWPN avec la configuration active et le multipathing hôte.';
 if(f?.evidenceConfidence==='CONFIGURED_OR_UNKNOWN')return 'Obtenir un export de zoning effectif et confirmer la zone active sur le switch.';
 if(f?.status==='UNKNOWN_WWPN')return 'Compléter les WWPN initiateur et cible du diagramme.';
 return 'Vérifier la couverture de l’export et collecter une preuve de zoning actif avant de conclure.';
}
export function filterSanEvidence(findings,level='ALL'){
 const allowed=['ALL','ACTIVE_DECLARED','CONFIGURED_OR_UNKNOWN','NONE'];
 const selected=allowed.includes(level)?level:'ALL';
 return (Array.isArray(findings)?findings:[]).filter(f=>selected==='ALL'||f.evidenceConfidence===selected);
}
