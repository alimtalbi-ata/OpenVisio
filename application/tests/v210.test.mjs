import test from 'node:test';
import assert from 'node:assert/strict';
import {DOCUMENT_KEY,saveDocumentWithBackup,recoverBackup} from '../src/unified-storage.js';
const deps={restoreGraph:JSON.parse,validateZones:x=>x,validateSanImport:x=>x};
const graph=JSON.stringify({nodes:[],edges:[]});
const storage=()=>{const m=new Map();return {getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,v),removeItem:k=>m.delete(k)};};
test('échec de remplacement restaure la sauvegarde précédente',()=>{
 const s=storage();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[1],null,deps);
 const before=s.getItem(DOCUMENT_KEY), backup=s.getItem(DOCUMENT_KEY+'-backup');
 const failing={...s,setItem(k,v){if(k===DOCUMENT_KEY)throw Error('disk full');s.setItem(k,v);}};
 assert.throws(()=>saveDocumentWithBackup(failing,DOCUMENT_KEY,graph,[2],null,deps),/disk full/);
 assert.equal(s.getItem(DOCUMENT_KEY),before);assert.equal(s.getItem(DOCUMENT_KEY+'-backup'),backup);
});
test('échec première mise à jour supprime la sauvegarde provisoire',()=>{
 const s=storage();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);
 const failing={...s,setItem(k,v){if(k===DOCUMENT_KEY)throw Error('quota');s.setItem(k,v);}};
 assert.throws(()=>saveDocumentWithBackup(failing,DOCUMENT_KEY,graph,[1],null,deps),/quota/);
 assert.equal(s.getItem(DOCUMENT_KEY+'-backup'),null);
});
test('écriture effective suivie d’une exception conserve le secours récupérable',()=>{
 const s=storage();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);
 const failing={...s,setItem(k,v){s.setItem(k,v);if(k===DOCUMENT_KEY)throw Error('interrupted');}};
 assert.throws(()=>saveDocumentWithBackup(failing,DOCUMENT_KEY,graph,[1],null,deps),/interrupted/);
 assert.deepEqual(recoverBackup(s,DOCUMENT_KEY,deps).document.zones,[]);
});
