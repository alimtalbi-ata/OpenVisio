// Auteur : Abdelhalim Talbi — validation de la persistance déclarative SAN.
export function validateZones(zones){
 if(!Array.isArray(zones)||zones.length>500)throw new Error('500 zones maximum');
 const seen=new Set();
 return zones.map(z=>{
  if(!z||typeof z!== 'object'||Array.isArray(z))throw new Error('Zone invalide');
  const name=String(z.name??'').trim(),fabric=String(z.fabric??'').toUpperCase();
  if(!name||name.length>128||!['A','B'].includes(fabric))throw new Error('Nom ou Fabric invalide');
  const key=fabric+':'+name.toLowerCase();if(seen.has(key))throw new Error('Zone dupliquée');seen.add(key);
  const check=values=>{if(!Array.isArray(values)||values.length>256)throw new Error('Membres invalides');return values.map(v=>{if(typeof v!=='string'||v.length>64)throw new Error('WWPN invalide');return v;});};
  return {name,fabric,initiators:check(z.initiators),targets:check(z.targets)};
 });
}
export function exportDiagram(state,zones){return {format:'openvisio-diagram',version:2,author:'Abdelhalim Talbi',nodes:state.nodes,edges:state.edges,groups:state.groups,layers:state.layers,zones:validateZones(zones)};}
export function importZones(data){return validateZones(data.zones??[]);}

/** Validate failure-domain metadata after a JSON save/open cycle without mutating the document. */
export function verifyFailureDomainRoundTrip(document){
 if(!document||!Array.isArray(document.nodes)||!Array.isArray(document.edges))throw new Error('Document invalide');
 const fields=['site','chassis','powerDomain','controller','failureDomain'];
 const before=[...document.nodes,...document.edges].map(item=>({id:item.id,values:Object.fromEntries(fields.filter(k=>Object.hasOwn(item,k)).map(k=>[k,item[k]]))}));
 const decoded=JSON.parse(JSON.stringify(document));
 const after=[...decoded.nodes,...decoded.edges];
 if(before.length!==after.length)throw new Error('Nombre de composants incohérent');
 for(let i=0;i<before.length;i++){
  if(before[i].id!==after[i].id)throw new Error('Identifiant modifié');
  for(const [key,value] of Object.entries(before[i].values)){
   if(typeof value!=='string'||value.length>256)throw new Error('Domaine invalide : '+key);
   if(after[i][key]!==value)throw new Error('Domaine perdu : '+key);
  }
 }
 return {verifiedComponents:after.length,verifiedDomains:before.reduce((sum,item)=>sum+Object.keys(item.values).length,0)};
}

/** Serialize a diagram and verify its SAN failure-domain metadata before writing. */
export function serializeSanDiagram(document){
 verifyFailureDomainRoundTrip(document);
 const json=JSON.stringify(document);
 if(typeof json!=='string')throw new Error('Sérialisation impossible');
 return json;
}
/** Parse saved diagram bytes and verify that all failure-domain values are safe. */
export function deserializeSanDiagram(json){
 if(typeof json!=='string'||!json.trim())throw new Error('Fichier JSON vide ou invalide');
 const doc=JSON.parse(json);
 verifyFailureDomainRoundTrip(doc);
 return doc;
}
