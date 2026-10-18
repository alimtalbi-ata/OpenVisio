import test from 'node:test';import assert from 'node:assert/strict';import {resolveZoneAliases,correlateSanImport} from '../src/san-import-correlation-v313.js';
test('explicit alias resolves WWPN',()=>{const z=resolveZoneAliases({aliases:[{name:'HOST',members:['10:00:00:00:00:00:00:01']}],zones:[{name:'z',members:['HOST','50:00:00:00:00:00:00:02']}]});assert.deepEqual(z[0].members,['10:00:00:00:00:00:00:01','50:00:00:00:00:00:00:02']);});
test('alias cycles terminate',()=>{const z=resolveZoneAliases({aliases:[{name:'A',members:['B']},{name:'B',members:['A']}],zones:[{name:'z',members:['A']}]});assert.deepEqual(z[0].members,[]);});
test('unknown state never marked active',()=>{const z=resolveZoneAliases({zones:[{name:'z',members:[]}]});assert.equal(z[0].configurationState,'unknown');});
test('explicit configured state retained',()=>{const z=resolveZoneAliases({zones:[{name:'z',members:[],configurationState:'configured'}]});assert.equal(z[0].configurationState,'configured');});
