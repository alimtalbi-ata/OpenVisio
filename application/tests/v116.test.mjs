import test from 'node:test';import assert from 'node:assert/strict';import {parsePorts,validateEdgePort,suggestedPorts} from '../src/ports.js';
test('liste des ports',()=>assert.deepEqual(parsePorts('eth0; FC0, vmnic0'),['eth0','FC0','vmnic0']));
test('ports dupliqués rejetés',()=>assert.throws(()=>parsePorts('eth0;ETH0')));
test('injection HTML rejetée',()=>assert.throws(()=>parsePorts('<script>')));
test('limite 64 ports',()=>assert.throws(()=>parsePorts(Array.from({length:65},(_,i)=>'p'+i).join(';'))));
test('ports vides autorisés',()=>assert.deepEqual(parsePorts(''),[]));
test('association valide',()=>assert.equal(validateEdgePort({sourceInterface:'FC0',targetInterface:'FC1'},{ports:['FC0']},{ports:['FC1']}),true));
test('association inconnue rejetée',()=>assert.equal(validateEdgePort({sourceInterface:'FC9'},{ports:['FC0']},{ports:[]}),false));
test('interfaces par type',()=>assert.ok(suggestedPorts('switch').includes('Gi1/0/1')));
