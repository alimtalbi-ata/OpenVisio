import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {serializeSanDiagram,deserializeSanDiagram} from '../src/zoning-document.js';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('editor JSON export uses validated SAN serializer',()=>assert.match(main,/const json=serializeSanDiagram\(\{\.\.\.exportDiagram\(state,declaredZones\)/));
test('editor JSON import uses validated SAN deserializer',()=>assert.match(main,/const data=deserializeSanDiagram\(await file\.text\(\)\)/));
test('failure domains survive editor-format export and import',()=>{const doc={format:'openvisio-diagram',nodes:[{id:'a',type:'switch',site:'PAR',powerDomain:'PDU-1'}],edges:[{id:'e',from:'a',to:'a',failureDomain:'DUCT-1'}],zones:[]};assert.deepEqual(deserializeSanDiagram(serializeSanDiagram(doc)),doc)});
test('serializer refuses invalid domain metadata before download',()=>assert.throws(()=>serializeSanDiagram({nodes:[{id:'a',site:123}],edges:[]}),/Domaine invalide/));
