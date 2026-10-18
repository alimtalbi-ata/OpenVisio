import test from 'node:test';
import assert from 'node:assert/strict';
import {buildSanImpactReport,sanImpactCsv} from '../src/san-impact-report.js';
const doc={nodes:[{id:'h',type:'server'},{id:'sa',type:'switch'},{id:'sb',type:'switch'},{id:'d',type:'storage'}],edges:[{id:'a1',from:'h',to:'sa',fabric:'A'},{id:'a2',from:'sa',to:'d',fabric:'A'},{id:'b1',from:'h',to:'sb',fabric:'B'},{id:'b2',from:'sb',to:'d',fabric:'B'}]};
test('fabric A failure preserves B and reports losses',()=>{const r=buildSanImpactReport(doc,{failedFabric:'A'});assert.equal(r.summary.pathsBefore,2);assert.equal(r.summary.pathsAfter,1);assert.equal(r.summary.disconnectedPairs,0);assert.deepEqual(r.visual.lostEdgeIds,['a1','a2']);});
test('switch loss reports remaining route',()=>{const r=buildSanImpactReport(doc,{failedNodeId:'sb'});assert.equal(r.summary.pathsAfter,1);});
test('both routes via shared host loss becomes disconnected',()=>{const r=buildSanImpactReport(doc,{failedNodeId:'h'});assert.equal(r.summary.disconnectedPairs,1);});
test('simulation does not mutate source',()=>{const before=JSON.stringify(doc);buildSanImpactReport(doc,{failedFabric:'B'});assert.equal(JSON.stringify(doc),before);});
test('CSV escapes spreadsheet formula prefixes',()=>{const r={affected:[{serverId:'=BAD',storageId:'d',before:1,after:0,lost:1,unreachable:true}]};assert.match(sanImpactCsv(r),/"'=BAD"/);});
