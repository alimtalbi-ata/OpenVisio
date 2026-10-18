// Auteur : Abdelhalim Talbi — modèle de zoning déclaratif, sans interrogation des fabrics.
export function normalizeWwpn(value){const s=String(value??'').replace(/[:-]/g,'').toUpperCase();return /^[0-9A-F]{16}$/.test(s)?s.match(/../g).join(':'):null;}
export function auditZoning(nodes,edges,zones=[]){
 const findings=[],matrix=[];const byId=new Map(nodes.map(n=>[n.id,n]));const seen=new Set();
 if(!Array.isArray(zones))return {matrix,findings:[{code:'invalid-zones',zone:''}]};
 for(const z of zones){
  const name=String(z?.name??'').trim(),fabric=String(z?.fabric??'').trim().toUpperCase();
  const initiators=Array.isArray(z?.initiators)?z.initiators:[],targets=Array.isArray(z?.targets)?z.targets:[];
  if(!name||!['A','B'].includes(fabric)){findings.push({code:'invalid-zone',zone:name});continue;}
  const key=fabric+':'+name.toLowerCase();if(seen.has(key))findings.push({code:'duplicate-zone',zone:name});seen.add(key);
  if(!initiators.length||!targets.length)findings.push({code:'incomplete-zone',zone:name});
  const normalized={initiators:[],targets:[]};
  for(const [kind,values] of [['initiators',initiators],['targets',targets]]){
   const unique=new Set();
   for(const value of values){const wwpn=normalizeWwpn(value);if(!wwpn){findings.push({code:'invalid-wwpn',zone:name,value:String(value)});continue;}
    if(unique.has(wwpn))findings.push({code:'duplicate-member',zone:name,value:wwpn});unique.add(wwpn);normalized[kind].push(wwpn);
   }
  }
  for(const initiator of normalized.initiators)for(const target of normalized.targets)matrix.push({zone:name,fabric,initiator,target});
 }
 const physical=new Set();
 for(const e of edges){const a=byId.get(e.from),b=byId.get(e.to);if(!a||!b)continue;
  const ai=normalizeWwpn(a.wwpn),bi=normalizeWwpn(b.wwpn);
  if(ai&&bi){physical.add(ai+'|'+bi);physical.add(bi+'|'+ai);}
 }
 // Une correspondance physique directe est un indice seulement : les chemins transitant par des switches ne sont pas ici résolus par WWPN.
 for(const row of matrix)if(!physical.has(row.initiator+'|'+row.target))findings.push({code:'unverified-physical-path',zone:row.zone,initiator:row.initiator,target:row.target});
 return {matrix,findings};
}
