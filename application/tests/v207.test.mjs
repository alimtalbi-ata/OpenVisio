import test from 'node:test';
import assert from 'node:assert/strict';
import {DOCUMENT_KEY,encodeDocument,decodeDocument,checksum,encodeBackup,decodeBackup,saveDocumentWithBackup,recoverBackup} from '../src/unified-storage.js';
const deps={restoreGraph:JSON.parse,validateZones:x=>x,validateSanImport:x=>x};
const graph=JSON.stringify({nodes:[{id:'A'}],edges:[]});
function store(){const data=new Map();return {data,getItem:k=>data.has(k)?data.get(k):null,setItem:(k,v)=>data.set(k,v)};}
test('empreinte stable',()=>assert.equal(checksum('abc'),checksum('abc')));
test('sauvegarde vérifiable',()=>assert.equal(decodeBackup(encodeBackup('abc')),'abc'));
test('altération de secours refusée',()=>assert.throws(()=>decodeBackup(encodeBackup('abc').replace('abc','abd')),/corrompue/));
test('première sauvegarde sans backup',()=>{const s=store();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);assert.equal(s.data.size,1);});
test('deuxième sauvegarde conserve état précédent',()=>{const s=store();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[{name:'zone'}],null,deps);assert.equal(recoverBackup(s,DOCUMENT_KEY,deps).document.zones.length,0);assert.equal(decodeDocument(s.getItem(DOCUMENT_KEY),deps).zones.length,1);});
test('document primaire invalide non promu en secours',()=>{const s=store();s.setItem(DOCUMENT_KEY,'{broken');assert.throws(()=>saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps));assert.equal(s.getItem(DOCUMENT_KEY),'{broken');assert.equal(s.data.size,1);});
test('copie absente retourne null',()=>assert.equal(recoverBackup(store(),DOCUMENT_KEY,deps),null));
test('récupération rejette un document interne invalide',()=>{const s=store();s.setItem(DOCUMENT_KEY+'-backup',encodeBackup('{}'));assert.throws(()=>recoverBackup(s,DOCUMENT_KEY,deps));});
test('échec écriture du backup laisse primaire intact',()=>{const s=store();saveDocumentWithBackup(s,DOCUMENT_KEY,graph,[],null,deps);const before=s.getItem(DOCUMENT_KEY);const failing={getItem:s.getItem,setItem:(k,v)=>{if(k.endsWith('-backup'))throw Error('quota');s.setItem(k,v);}};assert.throws(()=>saveDocumentWithBackup(failing,DOCUMENT_KEY,graph,[1],null,deps),/quota/);assert.equal(s.getItem(DOCUMENT_KEY),before);});
