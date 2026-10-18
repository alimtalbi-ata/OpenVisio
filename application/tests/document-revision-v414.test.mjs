import test from 'node:test';
import assert from 'node:assert/strict';
import {documentRevision,touchDocumentRevision,commitDocumentState,applyDocumentTransaction} from '../src/document-transaction.js';
test('revision is monotonic and not serialized',()=>{const d={nodes:[]};assert.equal(documentRevision(d),0);commitDocumentState(d,{nodes:[{id:'a'}]});assert.equal(documentRevision(d),1);assert.equal(JSON.stringify(d),'{"nodes":[{"id":"a"}]}');commitDocumentState(d,{nodes:[]});assert.equal(documentRevision(d),2)});
test('failed validation leaves source and revision intact',()=>{const d={nodes:[]};assert.throws(()=>applyDocumentTransaction(d,x=>x.nodes.push({id:'x'}),()=>false));assert.deepEqual(d,{nodes:[]});assert.equal(documentRevision(d),0)});
test('invalid revisions rejected',()=>{assert.throws(()=>documentRevision(null),TypeError);assert.throws(()=>touchDocumentRevision([]),TypeError)});
test('separate roots do not share revisions',()=>{const a={},b={};touchDocumentRevision(a);assert.equal(documentRevision(a),1);assert.equal(documentRevision(b),0)});
