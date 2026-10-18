import test from 'node:test';
import assert from 'node:assert/strict';
import {planZoningUpdate,commitZoningUpdate} from '../src/zoning-transaction.js';
const z=(name)=>[{name,fabric:'A',initiators:['10:00:00:00:00:00:00:01'],targets:['50:00:00:00:00:00:00:01']}];
test('zoning: changement validé avant checkpoint',()=>{let checkpoints=0,applied=null;const changed=commitZoningUpdate([],z('ZONE_A'),()=>checkpoints++,v=>applied=v);assert.equal(changed,true);assert.equal(checkpoints,1);assert.ok(applied);});
test('zoning: aucune entrée pour valeur identique',()=>{let checkpoints=0;const current=z('ZONE_A');assert.equal(commitZoningUpdate(current,current,()=>checkpoints++,()=>{}),false);assert.equal(checkpoints,0);});
test('zoning: entrée invalide sans mutation',()=>{let checkpoints=0;assert.throws(()=>commitZoningUpdate([],{},()=>checkpoints++,()=>{}));assert.equal(checkpoints,0);});
test('zoning: plan ne modifie pas la source',()=>{const current=[];planZoningUpdate(current,z('ZONE_A'));assert.deepEqual(current,[]);});
