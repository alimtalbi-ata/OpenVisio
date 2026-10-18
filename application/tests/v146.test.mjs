import test from 'node:test';import assert from 'node:assert/strict';import {validateSanEndToEnd,sanEndToEndCsv,sanEndToEndHtml} from '../src/san-end-to-end.js';
const doc={nodes:[{id:'s',type:'server',title:'Srv',wwpns:['10:00:00:00:00:00:00:01'],multipath:'MPIO'},{id:'t',type:'storage',title:'Array',luns:['L1'],lunMasking:[{lunId:'L1',initiatorWwpn:'10:00:00:00:00:00:00:01'}]}],edges:[{id:'e',from:'s',to:'t',fabric:'A',lunId:'L1',initiatorWwpn:'10:00:00:00:00:00:00:01',targetWwpn:'50:00:00:00:00:00:00:01',pathId:'p1'}]};
test('consolidated summary',()=>{const r=validateSanEndToEnd(doc);assert.equal(r.summary.total,1);assert.equal(r.summary.high,1)});
test('missing fabric redundancy',()=>assert.ok(validateSanEndToEnd(doc).rows[0].issues.includes('FABRIC_REDUNDANCY_NOT_DEMONSTRATED')));
test('CSV header',()=>assert.match(sanEndToEndCsv(validateSanEndToEnd(doc)),/Serveur/));
test('HTML scope',()=>assert.match(sanEndToEndHtml(validateSanEndToEnd(doc)),/documentaire/));
test('HTML escaping',()=>{const r=validateSanEndToEnd({...doc,nodes:[{...doc.nodes[0],title:'<script>'},doc.nodes[1]]});assert.ok(!sanEndToEndHtml(r).includes('<script>'))});
test('empty topology',()=>assert.equal(validateSanEndToEnd({nodes:[],edges:[]}).summary.total,0));
