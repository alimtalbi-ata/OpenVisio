import test from 'node:test';import assert from 'node:assert/strict';import {physicalPortMarkers,cableDiagnostics} from '../src/ports.js';
test('marqueurs dans le cadre',()=>{const m=physicalPortMarkers({w:120,h:60,ports:['FC0','FC1']});assert.equal(m.length,2);assert.ok(m.every(p=>p.x>0&&p.x<120&&p.y<60));});
test('marqueurs tronqués à 12',()=>assert.equal(physicalPortMarkers({w:120,h:60,ports:Array.from({length:30},(_,i)=>'p'+i)}).length,12));
test('géométrie invalide sans marqueur',()=>assert.deepEqual(physicalPortMarkers({w:0,h:50,ports:['FC0']}),[]));
test('câblage correct',()=>assert.deepEqual(cableDiagnostics([{id:'a',ports:['FC0']},{id:'b',ports:['FC1']}],[{id:'e',from:'a',to:'b',sourceInterface:'FC0',targetInterface:'FC1'}]),[]));
test('interface inconnue',()=>assert.ok(cableDiagnostics([{id:'a',ports:[]},{id:'b',ports:[]}],[{id:'e',from:'a',to:'b',sourceInterface:'FC0'}]).some(f=>f.code==='unknown-port')));
test('port réutilisé',()=>assert.ok(cableDiagnostics([{id:'a',ports:['FC0']},{id:'b',ports:['FC1']},{id:'c',ports:['FC2']}],[{id:'e1',from:'a',to:'b',sourceInterface:'FC0'},{id:'e2',from:'a',to:'c',sourceInterface:'FC0'}]).some(f=>f.code==='port-reused')));
test('extrémité absente',()=>assert.equal(cableDiagnostics([{id:'a',ports:[]}],[{id:'e',from:'a',to:'missing'}])[0].code,'missing-endpoint'));
