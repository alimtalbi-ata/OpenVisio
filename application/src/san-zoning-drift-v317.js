// OpenVisio v31.7 — comparaison documentaire actif/configuré. Auteur : Abdelhalim Talbi.
import {resolveZoneAliases} from './san-import-correlation-v313.js';
const key=z=>`${String(z.vsan??'unknown')}|${String(z.name??'').trim().toLowerCase()}`;
export function summarizeZoningEvidence(imported){
 const zones=resolveZoneAliases(imported);const grouped=new Map();
 for(const z of zones){const k=key(z);if(!grouped.has(k))grouped.set(k,{name:String(z.name??''),vsan:String(z.vsan??'unknown'),active:[],configured:[],unknown:[]});grouped.get(k)[z.configurationState]?.push(z);}
 const findings=[];
 for(const g of grouped.values()){
  const active=new Set(g.active.flatMap(z=>z.members));const configured=new Set(g.configured.flatMap(z=>z.members));
  let status='UNVERIFIED',recommendation='Collecter un export effectif et vérifier le VSAN/Fabric avant de conclure.';
  if(g.active.length&&g.configured.length){const missing=[...configured].filter(x=>!active.has(x));const extra=[...active].filter(x=>!configured.has(x));status=missing.length||extra.length?'MEMBERS_DIFFER':'MATCHED';recommendation=status==='MATCHED'?'Comparer avec le zoning effectif du switch et la configuration hôte.':'Examiner les membres ajoutés ou absents et confirmer la configuration effective.';findings.push({...g,status,missing,extra,recommendation});}
  else findings.push({...g,status,missing:[],extra:[],recommendation});
 }
 return {findings:findings.sort((a,b)=>a.vsan.localeCompare(b.vsan)||a.name.localeCompare(b.name)),counts:{matched:findings.filter(x=>x.status==='MATCHED').length,different:findings.filter(x=>x.status==='MEMBERS_DIFFER').length,unverified:findings.filter(x=>x.status==='UNVERIFIED').length},limitations:['Comparaison des seules zones présentes dans l’export','Absence de preuve ≠ panne ou suppression effective']};
}
export function zoningDriftCsv(report){const cell=x=>'"'+String(x??'').replaceAll('"','""').replace(/^[\s]*[=+@\-]/,"'$&")+'"';return [['vsan','zone','status','missing_from_active','only_in_active','recommendation'],...(report?.findings??[]).map(f=>[f.vsan,f.name,f.status,f.missing.join(';'),f.extra.join(';'),f.recommendation])].map(r=>r.map(cell).join(',')).join('\r\n');}
