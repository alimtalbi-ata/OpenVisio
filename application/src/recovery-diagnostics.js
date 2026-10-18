// Auteur : Abdelhalim Talbi — diagnostic sans mutation du stockage.
import {decodeDocument,decodeBackup} from './unified-storage.js';
export function inspectRecovery(storage,key,dependencies){
 const result={primary:'absent',backup:'absent',recoverable:false,issues:[]};
 for(const [name,storageKey,decode] of [['primary',key,raw=>decodeDocument(raw,dependencies)],['backup',key+'-backup',raw=>decodeDocument(decodeBackup(raw),dependencies)]]){
  try{const raw=storage.getItem(storageKey);if(raw===null)continue;decode(raw);result[name]='valid';}
  catch(e){result[name]='invalid';result.issues.push(name+': '+(e?.message||'lecture impossible'));}
 }
 result.recoverable=result.primary==='valid'||result.backup==='valid';
 return result;
}
