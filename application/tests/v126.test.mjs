import test from 'node:test';import assert from 'node:assert/strict';import {compareSanZones,assignSanRoles,parseSanConfig} from '../src/san-config-import.js';
const a='10:00:00:90:fa:12:34:56',b='20:00:00:90:fa:12:34:56';
test('comparaison zone nouvelle',()=>assert.equal(compareSanZones([{name:'Z',fabric:'A',initiators:[a],targets:[b]}],[])[0].status,'new'));
test('comparaison identique',()=>{const z={name:'Z',fabric:'A',initiators:[a],targets:[b]};assert.equal(compareSanZones([z],[z])[0].status,'identical')});
test('comparaison modifiée',()=>{const z={name:'Z',fabric:'A',initiators:[a],targets:[b]};assert.equal(compareSanZones([z],[{...z,targets:[]}])[0].status,'changed')});
test('Fabric distincte',()=>{const z={name:'Z',fabric:'A',initiators:[a],targets:[b]};assert.equal(compareSanZones([z],[{...z,fabric:'B'}])[0].status,'new')});
test('import et attribution explicite',()=>{const p=parseSanConfig(`alicreate "host","${a}"\nzonecreate "Z","host;${b}"`,'brocade','A');const z=assignSanRoles(p,{Z:{[a.toUpperCase()]:'initiator',[b.toUpperCase()]:'target'}});assert.equal(z[0].targets[0],b.toUpperCase())});
