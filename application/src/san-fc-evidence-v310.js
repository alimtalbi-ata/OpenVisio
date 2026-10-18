// OpenVisio v31.0 — audit documentaire des preuves SAN. Auteur : Abdelhalim Talbi.
// Ne jamais inférer un zoning/masking opérationnel d'une simple connexion graphique.
const norm=x=>String(x??'').trim().replaceAll(':','').toLowerCase();
const wwpn=x=>/^[0-9a-f]{16}$/.test(norm(x));
const setOf=x=>new Set((Array.isArray(x)?x:[]).map(norm).filter(Boolean));
export function correlateFcEvidence(trace,evidence={}){
 const zoning=Array.isArray(evidence.zones)?evidence.zones:[];
 const masking=Array.isArray(evidence.masking)?evidence.masking:[];
 const hosts=Array.isArray(evidence.hostPaths)?evidence.hostPaths:[];
 const findings=[];let verified=0,unknown=0;
 for(const [index,path] of (trace?.paths??[]).entries()){
  const first=path.hops?.[0],last=path.hops?.at(-1);
  const initiator=norm(first?.sourceWwpn),target=norm(last?.targetWwpn);
  const base={path:index+1,serverId:path.serverId??'',storageId:path.storageId??''};
  if(!wwpn(initiator)||!wwpn(target)){
   findings.push({...base,code:'ENDPOINT_WWPN_UNKNOWN',severity:'P2',detail:'WWPN initiateur ou cible absent/invalide : corrélation impossible'});unknown++;continue;
  }
  const matches=zoning.filter(z=>setOf(z.members).has(initiator)&&setOf(z.members).has(target));
  if(!zoning.length) {findings.push({...base,code:'ZONING_EVIDENCE_MISSING',severity:'P3',detail:'Aucun export de zoning fourni'});unknown++;}
  else if(!matches.length) findings.push({...base,code:'ZONING_PAIR_NOT_DOCUMENTED',severity:'P2',detail:'Paire initiateur/cible absente des zones fournies'});
  else verified++;
  if(!masking.length) findings.push({...base,code:'MASKING_EVIDENCE_MISSING',severity:'P3',detail:'Aucun export de masking fourni'});
  else if(!masking.some(m=>norm(m.initiatorWwpn)===initiator&&norm(m.targetWwpn)===target))findings.push({...base,code:'MASKING_PAIR_NOT_DOCUMENTED',severity:'P2',detail:'Paire initiateur/cible absente du masking fourni'});
  if(!hosts.length) findings.push({...base,code:'MULTIPATH_EVIDENCE_MISSING',severity:'P3',detail:'Aucune preuve multipathing hôte fournie'});
  else if(!hosts.some(h=>norm(h.serverId)===norm(path.serverId)&&norm(h.storageId)===norm(path.storageId)&&h.active===true))findings.push({...base,code:'ACTIVE_HOST_PATH_NOT_DOCUMENTED',severity:'P2',detail:'Aucun chemin actif correspondant dans les données hôte fournies'});
 }
 const counts={P1:0,P2:0,P3:0};for(const f of findings)counts[f.severity]++;
 return {findings,counts,matchedZonePaths:verified,unknownZonePaths:unknown,complete:!trace?.truncated,disclaimer:'Corrélation de déclarations importées, sans interrogation des équipements. Absence de preuve ≠ panne.'};
}
export function fcEvidenceCsv(result){const q=v=>'"'+String(v??'').replaceAll('"','""').replace(/^[=+@\-\t\r]/,"'$&")+'"';return [['path','server','storage','severity','code','detail'],...(result?.findings??[]).map(f=>[f.path,f.serverId,f.storageId,f.severity,f.code,f.detail])].map(r=>r.map(q).join(',')).join('\r\n')+'\r\n';}
