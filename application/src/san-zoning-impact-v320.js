// OpenVisio v32.0 — rapprochement conservateur des preuves FC. Auteur : Abdelhalim Talbi.
import {normalizeWwpn} from './san-config-import-v311.js';
import {resolveZoningTargets} from './san-zoning-navigation-v319.js';
const str=x=>String(x??'').trim();
const uniq=x=>[...new Set(x)].sort();
export function correlateZoningImpact(entry,snapshot){
 const base=resolveZoningTargets(entry,snapshot);
 const edges=Array.isArray(snapshot?.edges)?snapshot.edges:[];
 const wanted=uniq([...(entry?.missing??[]),...(entry?.extra??[])].map(normalizeWwpn).filter(Boolean));
 const matches=edges.filter(e=>[e.fromWwpn,e.toWwpn,e.sourceWwpn,e.targetWwpn].some(w=>wanted.includes(normalizeWwpn(w))));
 const edgeIds=uniq(matches.map(e=>str(e.id)).filter(Boolean));
 const nodeIds=uniq(matches.flatMap(e=>[str(e.from),str(e.to)]).filter(Boolean));
 const switchIds=base.ids;
 const status=!wanted.length?'NO_WWPN_EVIDENCE':!edgeIds.length?'NO_EXACT_CONNECTION_MATCH':base.status==='AMBIGUOUS'?'AMBIGUOUS_SWITCH':'DOCUMENTARY_MATCH';
 return {status,switchIds,edgeIds,nodeIds,wwpns:wanted,sourceLines:Array.isArray(entry?.sourceLines)?[...entry.sourceLines]:[],fabric:str(entry?.fabric),vsan:str(entry?.vsan),zone:str(entry?.zone),limitations:['Rapprochement par WWPN exact, sans preuve de zoning actif ni de panne','Un WWPN sur une connexion ne prouve pas l’appartenance de cette connexion à une zone']};
}
export function zoningImpactCsv(rows){const cell=x=>'"'+String(x??'').replace(/^[\s]*[=+@\-]/,"'$&").replaceAll('"','""')+'"';return [['fabric','vsan','zone','status','switch_ids','connection_ids','node_ids','wwpns','source_lines'],...(rows??[]).map(r=>[r.fabric,r.vsan,r.zone,r.status,r.switchIds.join(';'),r.edgeIds.join(';'),r.nodeIds.join(';'),r.wwpns.join(';'),r.sourceLines.join(';')])].map(row=>row.map(cell).join(',')).join('\r\n');}
