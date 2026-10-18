import test from 'node:test';import assert from 'node:assert/strict';import {correlateSanImport,sanCorrelationCsv} from '../src/san-import-correlation-v313.js';
test('empty topology yields no invented findings',()=>{assert.deepEqual(correlateSanImport({nodes:[],edges:[]},{zones:[]}).findings,[])});
test('empty evidence never proves a failure',()=>{const r=correlateSanImport({nodes:[],edges:[]},{zones:[]});assert.match(r.limitations[0],/absence/)});
test('CSV header and formula escaping',()=>{const csv=sanCorrelationCsv({findings:[{path:1,serverId:'=danger',storageId:'S',status:'REVIEW',zoneNames:[],edgeIds:[]}]});assert.match(csv,/"'=danger"/);assert.match(csv,/initiator_wwpn/)});
test('malformed imported zones do not crash on empty topology',()=>{assert.equal(correlateSanImport({nodes:[],edges:[]},{zones:[null]}).findings.length,0)});
