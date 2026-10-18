// Auteur : Abdelhalim Talbi — sauvegarde portable, contrôle et prévalidation.
import {checksum,decodeDocument,encodeDocument} from './unified-storage.js';
export const PORTABLE_FORMAT='openvisio-portable-backup';
export async function exportPortableBackup(graph,zones,sanImport){
 const document=encodeDocument(graph,zones,sanImport);
 return JSON.stringify({format:PORTABLE_FORMAT,version:2,integrity:{algorithm:'sha256',value:await sha256(document)},document});
}
export async function inspectPortableBackup(raw,dependencies){
 if(typeof raw!=='string'||raw.length>20_000_000)throw Error('Fichier de sauvegarde trop volumineux ou invalide');
 const envelope=JSON.parse(raw);
 if(envelope?.format!==PORTABLE_FORMAT||![1,2].includes(envelope.version)||typeof envelope.document!=='string')throw Error('Format de sauvegarde inconnu');
 if(envelope.version===2){if(envelope.integrity?.algorithm!=='sha256'||envelope.integrity.value!==await sha256(envelope.document))throw Error('Intégrité SHA-256 de la sauvegarde non vérifiée');}
 else if(envelope.integrity?.algorithm!=='fnv1a32'||envelope.integrity.value!==checksum(envelope.document))throw Error('Intégrité de la sauvegarde non vérifiée');
 const document=decodeDocument(envelope.document,dependencies);
 return {rawDocument:envelope.document,document,summary:{nodes:document.graph.nodes.length,edges:document.graph.edges.length,zones:document.zones.length}};
}
export function restorePortableBackup(storage,key,inspection,dependencies){
 // Revalider au dernier instant et ne jamais modifier le stockage en cas d'erreur.
 const checked=decodeDocument(inspection.rawDocument,dependencies);
 const old=storage.getItem(key);
 if(old===inspection.rawDocument)return {changed:false,document:checked};
 if(old!==null){
  // Conserver uniquement les anciens documents valides en secours.
  decodeDocument(old,dependencies);
  storage.setItem(key+'-backup',JSON.stringify({schema:1,checksum:checksum(old),document:old}));
 }
 storage.setItem(key,inspection.rawDocument);
 return {changed:true,document:checked};
}

export async function sha256(raw){
 if(typeof raw!=='string')throw Error('Contenu invalide');
 if(!globalThis.crypto?.subtle)throw Error('SHA-256 indisponible : navigateur sécurisé (HTTPS ou localhost) requis');
 const bytes=new TextEncoder().encode(raw);
 const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);
 return Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
}
