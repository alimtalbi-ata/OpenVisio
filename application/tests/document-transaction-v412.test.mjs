import test from 'node:test';
import assert from 'node:assert/strict';
import {applyDocumentTransaction,commitDocumentState} from '../src/document-transaction.js';
test('transaction isolée du document original',()=>{const a={nodes:[{id:'A',x:0}]};const b=applyDocumentTransaction(a,d=>{d.nodes[0].x=42},d=>d.nodes.length===1);assert.equal(a.nodes[0].x,0);assert.equal(b.nodes[0].x,42)});
test('transaction refusée sans mutation',()=>{const a={nodes:[]};assert.throws(()=>applyDocumentTransaction(a,d=>d.nodes.push({id:'A'}),()=>false));assert.deepEqual(a,{nodes:[]})});
test('erreur de mutation sans effet',()=>{const a={nodes:[]};assert.throws(()=>applyDocumentTransaction(a,d=>{d.nodes.push(1);throw Error('échec')},()=>true));assert.deepEqual(a,{nodes:[]})});
test('commit retire les clés obsolètes',()=>{const a={old:1,nodes:[]};commitDocumentState(a,{nodes:[1]});assert.deepEqual(a,{nodes:[1]})});
test('commit refuse les types incorrects',()=>assert.throws(()=>commitDocumentState([],{})));
