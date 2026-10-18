import test from 'node:test';
import assert from 'node:assert/strict';
import {importSanConfiguration} from '../src/san-config-import-v311.js';
import {resolveZoneAliases} from '../src/san-import-correlation-v313.js';
test('Brocade effective section explicitly active',()=>{const x=importSanConfiguration('Effective configuration:\n zone: Z1 10:00:00:00:00:00:00:01;50:00:00:00:00:00:00:02');assert.equal(x.zones[0].configurationState,'active');});
test('Brocade configured section never inferred active',()=>{const x=importSanConfiguration('Defined configuration:\n zone: Z1 10:00:00:00:00:00:00:01');assert.equal(x.zones[0].configurationState,'unknown');});
test('Cisco zone configured not asserted active',()=>{const x=importSanConfiguration('zone name Z1 vsan 10\n member pwwn 10:00:00:00:00:00:00:01');assert.equal(x.zones[0].configurationState,'configured');assert.equal(x.zones[0].vsan,'10');assert.ok(x.zones[0].members.includes('10:00:00:00:00:00:00:01'));});
test('Cisco fcalias member is retained',()=>{const x=importSanConfiguration('fcalias name HOST vsan 10\n member pwwn 10:00:00:00:00:00:00:01');assert.ok(x.aliases[0].members.includes('10:00:00:00:00:00:00:01'));});
test('Unknown alias does not manufacture zone member',()=>{const z=resolveZoneAliases({zones:[{name:'Z',members:['MISSING']}]});assert.deepEqual(z[0].members,[]);});
