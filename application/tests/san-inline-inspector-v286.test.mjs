import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectSanSelection} from '../src/san-inline-inspector.js';
import {filterSanLines} from '../src/san-inspector-filter.js';
const state={nodes:[{id:'host',label:'ESXi',wwpn:'10:00:00:00:00:00:00:01',port:'vmhba1'},{id:'switch',label:'SAN A'}],edges:[{id:'fc1',from:'host',to:'switch',fabric:'A',fcPort:'1/12',portWwpn:'20:00:00:00:00:00:00:02'}]};
test('documented FC ports and WWPN displayed',()=>{const r=inspectSanSelection(state,'host');assert.ok(r.lines.some(x=>x.includes('vmhba1')));assert.ok(r.lines.some(x=>x.includes('1/12')));assert.ok(r.lines.some(x=>x.includes('10:00:00:00:00:00:00:01')));});
test('invalid WWPN explicitly flagged',()=>{const r=inspectSanSelection({...state,nodes:[{...state.nodes[0],wwpn:'invalid'},state.nodes[1]]},'host');assert.ok(r.lines.some(x=>x.includes('format WWPN invalide')));});
test('fabric A filter excludes unrelated lines',()=>{assert.deepEqual(filterSanLines(['Identifiant : X','Fabric A : 1','Fabric B : 0'],'A'),['Fabric A : 1']);});
test('no mutation of topology',()=>{const before=JSON.stringify(state);inspectSanSelection(state,'host');assert.equal(JSON.stringify(state),before);});
