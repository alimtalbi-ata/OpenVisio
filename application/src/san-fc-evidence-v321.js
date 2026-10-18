// OpenVisio v32.1 — preuves multi-attributs FC, sans extrapolation. Auteur : Abdelhalim Talbi.
import {normalizeWwpn} from './san-config-import-v311.js';
const value=x=>String(x??'').trim();
const unique=xs=>[...new Set(xs.filter(Boolean))].sort();
const port=x=>value(x).toLowerCase().replace(/\s+/g,'');
const fabric=x=>value(x).toUpperCase();
const wwpn=x=>normalizeWwpn(x)||'';
export function evaluateFcEvidence(entry, snapshot){
 const edges=Array.isArray(snapshot?.edges)?snapshot.edges:[];
 const wanted=unique([...(entry?.missing??[]),...(entry?.extra??[]),...(entry?.wwpns??[])].map(wwpn));
 const desiredPort=port(entry?.port), desiredFabric=fabric(entry?.fabric);
 const results=[];
 for(const edge of edges){
  const edgeWwpns=unique([edge.fromWwpn,edge.toWwpn,edge.sourceWwpn,edge.targetWwpn].map(wwpn));
  const matched= wanted.filter(w=>edgeWwpns.includes(w));
  if(!matched.length)continue;
  const ports=unique([edge.fromPort,edge.toPort,edge.sourcePort,edge.targetPort].map(port));
  const portKnown=Boolean(desiredPort&&ports.length);
  const portMatches=portKnown&&ports.includes(desiredPort);
  const edgeFabric=fabric(edge.fabric);
  const fabricKnown=Boolean(desiredFabric&&edgeFabric);
  const fabricMatches=fabricKnown&&desiredFabric===edgeFabric;
  const contradictions=(portKnown&&!portMatches)||(fabricKnown&&!fabricMatches);
  const status=contradictions?'CONFLICT':portMatches&&fabricMatches?'CORROBORATED':'PARTIAL';
  results.push({edgeId:value(edge.id),status,matchedWwpns:matched,portEvidence:portKnown?(portMatches?'MATCH':'CONFLICT'):'UNKNOWN',fabricEvidence:fabricKnown?(fabricMatches?'MATCH':'CONFLICT'):'UNKNOWN',isl:Boolean(edge.isl||edge.type==='isl'),from:value(edge.from),to:value(edge.to)});
 }
 results.sort((a,b)=>a.edgeId.localeCompare(b.edgeId));
 const status=!wanted.length?'NO_WWPN_EVIDENCE':!results.length?'NO_MATCH':results.some(r=>r.status==='CONFLICT')?'CONFLICT':results.some(r=>r.status==='CORROBORATED')?'CORROBORATED':'PARTIAL';
 return {status,results,requestedWwpns:wanted,limitations:['Correspondance documentaire uniquement : aucune preuve de zoning actif, de connectivité physique ou de multipathing','Les champs port et Fabric absents restent inconnus']};
}
export function fcEvidenceCsv(reports){
 const cell=x=>'"'+value(x).replace(/^[\s]*[=+@\-]/,"'$&").replaceAll('"','""')+'"';
 const rows=[['status','edge_id','wwpns','port_evidence','fabric_evidence','isl','from','to']];
 for(const report of reports??[])for(const r of report.results??[])rows.push([r.status,r.edgeId,r.matchedWwpns.join(';'),r.portEvidence,r.fabricEvidence,r.isl,r.from,r.to]);
 return rows.map(row=>row.map(cell).join(',')).join('\r\n');
}
