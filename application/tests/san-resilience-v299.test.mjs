import test from 'node:test';import assert from 'node:assert/strict';
import {buildResilienceMatrix,exportResilienceCsv} from '../src/san-resilience-matrix-v299.js';
const doc={nodes:[{id:'h',type:'server'},{id:'a',type:'switch'},{id:'b',type:'switch'},{id:'s',type:'storage'}],edges:[{id:'1',from:'h',to:'a',fabric:'A'},{id:'2',from:'a',to:'s',fabric:'A'},{id:'3',from:'h',to:'b',fabric:'B'},{id:'4',from:'b',to:'s',fabric:'B'}]};
test('independent dual fabric',()=>{const x=buildResilienceMatrix(doc);assert.equal(x.rows[0].priority,'P4');assert.equal(x.rows[0].independentDocumented,true)});
test('missing B is P1',()=>{const x=buildResilienceMatrix({...doc,edges:doc.edges.slice(0,2)});assert.equal(x.rows[0].priority,'P1')});
test('does not mutate input',()=>{const s=JSON.stringify(doc);buildResilienceMatrix(doc);assert.equal(JSON.stringify(doc),s)});
test('CSV escapes spreadsheet formulas',()=>{const csv=exportResilienceCsv({rows:[{serverId:'=CMD()',storageId:'s',fabricA:1,fabricB:0,priority:'P1',sharedTransitIds:[],recommendations:[]}]});assert.match(csv,/"'=CMD\(\)"/)});
