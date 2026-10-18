import test from 'node:test';
import assert from 'node:assert/strict';
import {portInventory,cableDiagnostics} from '../src/ports.js';
const nodes=[{id:'a',ports:['FC0','FC1'],title:'Hôte'},{id:'b',ports:['FC0'],title:'Baie'}];
test('inventaire SAN : ports libres et utilisés',()=>{const r=portInventory(nodes,[{id:'e',from:'a',to:'b',sourceInterface:'FC0',targetInterface:'FC0'}]);assert.deepEqual(r.map(x=>x.status),['used','free','used']);});
test('inventaire SAN : conflits de ports détectés',()=>{const r=portInventory(nodes,[{id:'e1',from:'a',to:'b',sourceInterface:'FC0',targetInterface:'FC0'},{id:'e2',from:'a',to:'b',sourceInterface:'FC0',targetInterface:'FC0'}]);assert.equal(r[0].status,'conflict');assert.equal(r[0].edgeIds.length,2);assert.ok(r[0].findings.some(x=>x.code==='port-reused'));});
test('inventaire SAN : lien réflexif non doublé',()=>{const r=portInventory([{id:'a',ports:['FC0']}],[{id:'loop',from:'a',to:'a',sourceInterface:'FC0',targetInterface:'FC0'}]);assert.deepEqual(r[0].edgeIds,['loop']);});
test('inventaire SAN : préserve les anomalies de câblage',()=>{const edges=[{id:'e',from:'a',to:'b',sourceInterface:'FC0',targetInterface:'eth0'}];const r=portInventory(nodes,edges);assert.deepEqual(r[0].findings,cableDiagnostics(nodes,edges));});
test('inventaire SAN : grand nombre de ports et connexions',()=>{const many=Array.from({length:150},(_,i)=>({id:'n'+i,ports:Array.from({length:40},(_,j)=>'FC'+j)}));const links=Array.from({length:149},(_,i)=>({id:'e'+i,from:'n'+i,to:'n'+(i+1),sourceInterface:'FC0',targetInterface:'FC1'}));const r=portInventory(many,links);assert.equal(r.length,6000);assert.equal(r.filter(x=>x.status==='used').length,298);});
