import test from 'node:test';import assert from 'node:assert/strict';
import {correlateZoningImpact,zoningImpactCsv} from '../src/san-zoning-impact-v320.js';
const w='10:00:00:00:00:00:00:01';
test('identifie uniquement les connexions portant le WWPN exact',()=>{const r=correlateZoningImpact({switch:'SW1',missing:[w],zone:'z',sourceLines:[8]}, {nodes:[{id:'s',name:'SW1'}],edges:[{id:'e',from:'a',to:'s',sourceWwpn:w},{id:'other',from:'b',to:'c',sourceWwpn:'20:00:00:00:00:00:00:01'}]});assert.deepEqual(r.edgeIds,['e']);assert.deepEqual(r.nodeIds,['a','s']);assert.deepEqual(r.sourceLines,[8]);});
test('sans WWPN, aucune correspondance inventée',()=>{const r=correlateZoningImpact({switch:'SW1'}, {nodes:[{id:'s',name:'SW1'}],edges:[{id:'e'}]});assert.equal(r.status,'NO_WWPN_EVIDENCE');assert.deepEqual(r.edgeIds,[]);});
test('switch ambigu non localisé',()=>{const r=correlateZoningImpact({switch:'SW1',extra:[w]}, {nodes:[{id:'a',name:'SW1'},{id:'b',name:'SW1'}],edges:[]});assert.deepEqual(r.switchIds,[]);});
test('export CSV protège les formules',()=>{const csv=zoningImpactCsv([{fabric:'=evil',vsan:'1',zone:'z',status:'x',switchIds:[],edgeIds:[],nodeIds:[],wwpns:[],sourceLines:[]}]);assert.match(csv,/"'=evil"/);});
