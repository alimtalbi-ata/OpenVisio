import test from 'node:test';
import assert from 'node:assert/strict';
import {correlateFcEvidence,fcEvidenceCsv} from '../src/san-fc-evidence-v310.js';
const trace={paths:[{serverId:'esx',storageId:'array',hops:[{sourceWwpn:'10:00:00:00:00:00:00:01'},{targetWwpn:'50:00:00:00:00:00:00:01'}]}]};
test('evidence complete yields no findings',()=>{const x=correlateFcEvidence(trace,{zones:[{members:['1000000000000001','5000000000000001']}],masking:[{initiatorWwpn:'1000000000000001',targetWwpn:'5000000000000001'}],hostPaths:[{serverId:'esx',storageId:'array',active:true}]});assert.equal(x.findings.length,0);assert.equal(x.matchedZonePaths,1);});
test('missing evidence is unknown, not failure',()=>{const x=correlateFcEvidence(trace);assert.deepEqual(x.findings.map(f=>f.code),['ZONING_EVIDENCE_MISSING','MASKING_EVIDENCE_MISSING','MULTIPATH_EVIDENCE_MISSING']);});
test('mismatched evidence is documented not actual outage',()=>{const x=correlateFcEvidence(trace,{zones:[{members:['1111111111111111','2222222222222222']}],masking:[{}],hostPaths:[{active:false}]});assert.equal(x.findings.filter(f=>f.severity==='P2').length,3);});
test('invalid endpoint WWPN stops correlation',()=>{const x=correlateFcEvidence({paths:[{hops:[{sourceWwpn:'invalid'}]}]});assert.equal(x.findings[0].code,'ENDPOINT_WWPN_UNKNOWN');});
test('CSV quotes and neutralizes formulas',()=>{const x=fcEvidenceCsv({findings:[{detail:'=2+2',code:'X'}]});assert.match(x,/"'=2\+2"/);});
