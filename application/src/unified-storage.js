// Auteur : Abdelhalim Talbi — persistance atomique d’un document et de ses métadonnées SAN.
export const DOCUMENT_KEY='openvisio-document-v206';
export function encodeDocument(graph,zones,sanImport){
 if(typeof graph!=='string')throw Error('Instantané de diagramme invalide');
 const parsed=JSON.parse(graph);
 if(!parsed||typeof parsed!=='object'||!Array.isArray(parsed.nodes)||!Array.isArray(parsed.edges))throw Error('Diagramme invalide');
 if(!Array.isArray(zones))throw Error('Zoning invalide');
 return JSON.stringify({schema:1,graph:parsed,zones,sanImport:sanImport??null});
}
export function decodeDocument(raw,{restoreGraph,validateZones,validateSanImport}){
 const data=JSON.parse(raw);
 if(!data||data.schema!==1||!data.graph||!Array.isArray(data.zones))throw Error('Document unifié invalide');
 // Toutes les validations précèdent la première modification du modèle actif.
 const graph=restoreGraph(JSON.stringify(data.graph));
 const zones=validateZones(data.zones);
 const sanImport=validateSanImport(data.sanImport??null);
 return {graph,zones,sanImport};
}
export function saveDocument(storage,key,graph,zones,sanImport){
 const encoded=encodeDocument(graph,zones,sanImport);
 storage.setItem(key,encoded); // Une seule écriture : pas d’état SAN partiellement enregistré.
 return encoded;
}

// v20.7 : une copie de secours validée précède chaque remplacement.
export const BACKUP_KEY=DOCUMENT_KEY+'-backup';
export function checksum(raw){let h=2166136261;for(let i=0;i<raw.length;i++){h^=raw.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0).toString(16).padStart(8,'0');}
export function encodeBackup(raw){return JSON.stringify({schema:1,checksum:checksum(raw),document:raw});}
export function decodeBackup(raw){const data=JSON.parse(raw);if(data?.schema!==1||typeof data.document!=='string'||data.checksum!==checksum(data.document))throw Error('Copie de secours corrompue');return data.document;}
export function saveDocumentWithBackup(storage,key,graph,zones,sanImport,dependencies){
 const encoded=encodeDocument(graph,zones,sanImport);
 const previous=storage.getItem(key);
 if(previous===encoded)return encoded;
 if(previous!==null){
  // Ne jamais promouvoir une version primaire corrompue en sauvegarde.
  decodeDocument(previous,dependencies);
  const backupKey=key+'-backup';
  const priorBackup=storage.getItem(backupKey);
  storage.setItem(backupKey,encodeBackup(previous));
  try{storage.setItem(key,encoded);}
  catch(error){
   // Si le primaire n'a pas été remplacé, rétablir l'ancien secours.
   // Si l'écriture a réussi avant de lever une exception, conserver le secours récent.
   try{if(storage.getItem(key)===previous){
    if(priorBackup===null)storage.removeItem(backupKey);
    else storage.setItem(backupKey,priorBackup);
   }}catch{}
   throw error;
  }
  return encoded;
 }
 storage.setItem(key,encoded);
 return encoded;
}
export function recoverBackup(storage,key,dependencies){
 const backup=storage.getItem(key+'-backup');
 if(backup===null)return null;
 const raw=decodeBackup(backup);
 return {raw,document:decodeDocument(raw,dependencies)};
}
