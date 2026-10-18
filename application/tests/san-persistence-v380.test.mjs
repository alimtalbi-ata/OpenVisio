import test from 'node:test';
import assert from 'node:assert/strict';
import {exportDiagram,verifyFailureDomainRoundTrip} from '../src/zoning-document.js';
const fields={site:'PAR-01',chassis:'CH-01',powerDomain:'PDU-A',controller:'CTRL-1',failureDomain:'RISK-01'};
const state={nodes:[{id:'n1',type:'server',...fields},{id:'n2',type:'storage'}],edges:[{id:'e1',from:'n1',to:'n2',...fields}],groups:[],layers:[]};
test('JSON save/open retains all five node and edge SAN domains',()=>{const document=exportDiagram(state,[]);const result=verifyFailureDomainRoundTrip(document);assert.deepEqual(result,{verifiedComponents:3,verifiedDomains:10});assert.deepEqual(JSON.parse(JSON.stringify(document)).edges[0].powerDomain,'PDU-A');});
test('empty domains are valid and no fields are injected',()=>{assert.deepEqual(verifyFailureDomainRoundTrip({nodes:[{id:'a'}],edges:[]}),{verifiedComponents:1,verifiedDomains:0});});
test('invalid domain values fail closed',()=>{assert.throws(()=>verifyFailureDomainRoundTrip({nodes:[{id:'a',site:{unexpected:true}}],edges:[]}),/Domaine invalide/);});
test('verification does not mutate original document',()=>{const doc=exportDiagram(state,[]);const snapshot=JSON.stringify(doc);verifyFailureDomainRoundTrip(doc);assert.equal(JSON.stringify(doc),snapshot);});
