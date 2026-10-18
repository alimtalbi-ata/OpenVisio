import test from 'node:test';
import assert from 'node:assert/strict';
import {serializeSanDiagram,deserializeSanDiagram} from '../src/zoning-document.js';
const doc={format:'openvisio-diagram',nodes:[{id:'sw-a',site:'PAR',powerDomain:'PDU-1'},{id:'sw-b',site:'PAR',powerDomain:'PDU-2'}],edges:[{id:'fiber-a',from:'sw-a',to:'sw-b',failureDomain:'DUCT-1'}],groups:[],layers:[]};
test('save/reopen preserves equipment and link failure domains',()=>{const restored=deserializeSanDiagram(serializeSanDiagram(doc));assert.deepEqual(restored,doc);assert.notStrictEqual(restored,doc);});
test('save/reopen does not mutate original topology',()=>{const before=JSON.stringify(doc);deserializeSanDiagram(serializeSanDiagram(doc));assert.equal(JSON.stringify(doc),before);});
test('reject malformed saved JSON and invalid document shape',()=>{assert.throws(()=>deserializeSanDiagram('{oops'));assert.throws(()=>deserializeSanDiagram('null'),/Document invalide/);assert.throws(()=>deserializeSanDiagram('{"nodes":[],"edges":{}}'),/Document invalide/);});
test('reject nonstring failure domains both on save and reopen',()=>{const bad={nodes:[{id:'x',powerDomain:42}],edges:[]};assert.throws(()=>serializeSanDiagram(bad),/Domaine invalide/);assert.throws(()=>deserializeSanDiagram(JSON.stringify(bad)),/Domaine invalide/);});
test('reject missing or empty JSON payload',()=>{assert.throws(()=>deserializeSanDiagram(''),/vide/);assert.throws(()=>deserializeSanDiagram(undefined),/vide/);});
