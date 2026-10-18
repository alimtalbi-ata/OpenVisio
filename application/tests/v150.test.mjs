import test from 'node:test';import assert from 'node:assert/strict';import {analyzeSanSpof,spofCsv,spofHtml} from '../src/san-spof.js';
const doc={nodes:[{id:'s',title:'Serveur',type:'server'},{id:'t',title:'Stockage',type:'storage'}],edges:[{id:'e',from:'s',to:'t',fabric:'A'}]};
test('analyse retourne les cibles',()=>{assert.ok(analyzeSanSpof(doc).results.length>=1)});
test('aucune mutation du document',()=>{const old=JSON.stringify(doc);analyzeSanSpof(doc);assert.equal(JSON.stringify(doc),old)});
test('limite de cibles',()=>assert.throws(()=>analyzeSanSpof(doc,{maxTargets:1}),/Trop de cibles/));
test('CSV possède un en-tête',()=>assert.match(spofCsv(analyzeSanSpof(doc)),/Identifiant/));
test('HTML possède un titre',()=>assert.match(spofHtml(analyzeSanSpof(doc)),/points uniques/));
test('HTML échappe le nom',()=>{const d=structuredClone(doc);d.nodes[0].title='<script>';assert.ok(!spofHtml(analyzeSanSpof(d)).includes('<script>'))});
