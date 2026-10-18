import test from 'node:test';
import assert from 'node:assert/strict';
import {exportPortableBackup,inspectPortableBackup,restorePortableBackup,sha256} from '../src/portable-backup.js';
import {DOCUMENT_KEY,decodeDocument,checksum} from '../src/unified-storage.js';
const deps={restoreGraph:JSON.parse,validateZones:x=>{if(!Array.isArray(x))throw Error('zones');return x;},validateSanImport:x=>x};
const graph=JSON.stringify({nodes:[{id:'A'}],edges:[]});
const portable=()=>exportPortableBackup(graph,[{name:'Z'}],null);
function store(){const map=new Map();return {getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,v),map};}
test('SHA-256 vecteur standard',async()=>assert.equal(await sha256('abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'));
test('export portable SHA-256 round-trip diagramme et zoning',async()=>{const raw=await portable(),x=await inspectPortableBackup(raw,deps);assert.equal(JSON.parse(raw).integrity.algorithm,'sha256');assert.equal(x.summary.nodes,1);assert.equal(x.summary.zones,1);});
test('corruption document rejetée',async()=>{const e=JSON.parse(await portable());e.document=e.document.replace('"A"','"B"');await assert.rejects(inspectPortableBackup(JSON.stringify(e),deps),/Intégrité/);});
test('format étranger rejeté',async()=>await assert.rejects(inspectPortableBackup('{}',deps),/Format/));
test('empreinte manquante rejetée',async()=>{const e=JSON.parse(await portable());delete e.integrity;await assert.rejects(inspectPortableBackup(JSON.stringify(e),deps),/Intégrité/);});
test('limite taille fichier appliquée',async()=>await assert.rejects(inspectPortableBackup('x'.repeat(20_000_001),deps),/volumineux/));
test('restauration et sauvegarde de l’ancien document',async()=>{const s=store();const old=await exportPortableBackup(JSON.stringify({nodes:[],edges:[]}),[],null);s.setItem(DOCUMENT_KEY,(await inspectPortableBackup(old,deps)).rawDocument);const result=restorePortableBackup(s,DOCUMENT_KEY,await inspectPortableBackup(await portable(),deps),deps);assert.equal(result.changed,true);assert.equal(decodeDocument(s.getItem(DOCUMENT_KEY),deps).zones.length,1);assert.ok(s.getItem(DOCUMENT_KEY+'-backup'));});
test('document identique ne génère pas de sauvegarde',async()=>{const s=store(),i=await inspectPortableBackup(await portable(),deps);s.setItem(DOCUMENT_KEY,i.rawDocument);assert.equal(restorePortableBackup(s,DOCUMENT_KEY,i,deps).changed,false);assert.equal(s.map.size,1);});
test('ancien primaire corrompu bloque remplacement',async()=>{const s=store();s.setItem(DOCUMENT_KEY,'{invalid');const i=await inspectPortableBackup(await portable(),deps);assert.throws(()=>restorePortableBackup(s,DOCUMENT_KEY,i,deps));assert.equal(s.getItem(DOCUMENT_KEY),'{invalid');});
test('échec écriture secours conserve primaire',async()=>{const s=store();const old=(await inspectPortableBackup(await exportPortableBackup(JSON.stringify({nodes:[],edges:[]}),[],null),deps)).rawDocument;s.setItem(DOCUMENT_KEY,old);const failing={getItem:s.getItem,setItem:(k,v)=>{if(k.endsWith('-backup'))throw Error('quota');s.setItem(k,v);}};const i=await inspectPortableBackup(await portable(),deps);assert.throws(()=>restorePortableBackup(failing,DOCUMENT_KEY,i,deps),/quota/);assert.equal(s.getItem(DOCUMENT_KEY),old);});
test('compatibilité sauvegarde portable v1',async()=>{const e=JSON.parse(await portable());e.version=1;e.integrity={algorithm:'fnv1a32',value:checksum(e.document)};assert.equal((await inspectPortableBackup(JSON.stringify(e),deps)).summary.nodes,1);});
