import test from 'node:test';import assert from 'node:assert/strict';import {auditFcTrace,auditFcCsv} from '../src/san-fc-audit-v309.js';
const hop=(x={})=>({edgeId:'e1',from:'s',to:'t',sourcePort:'1',targetPort:'2',sourceWwpn:'10:00:00:00:00:00:00:01',targetWwpn:'10:00:00:00:00:00:00:02',fabric:'A',isl:false,...x});
test('valid FC path has no findings',()=>assert.equal(auditFcTrace({paths:[{hops:[hop()]}]}).findings.length,0));
test('invalid WWPN detected',()=>assert.ok(auditFcTrace({paths:[{hops:[hop({sourceWwpn:'bad'})]}]}).findings.some(f=>f.code==='WWPN_INVALID')));
test('cross fabric flagged P1',()=>assert.equal(auditFcTrace({paths:[{hops:[hop(),hop({edgeId:'e2',from:'t',to:'u',fabric:'B'})]}]}).counts.P1,1));
test('discontinuous nodes flagged',()=>assert.ok(auditFcTrace({paths:[{hops:[hop(),hop({from:'other'})]}]}).findings.some(f=>f.code==='PATH_DISCONTINUITY')));
test('missing ISL port flagged',()=>assert.ok(auditFcTrace({paths:[{hops:[hop({isl:true,sourcePort:''})]}]}).findings.some(f=>f.code==='ISL_PORT_MISSING')));
test('CSV escapes formula injection',()=>assert.match(auditFcCsv({findings:[{edgeId:'=SUM(1)',path:1,hop:1,severity:'P2',code:'X',detail:'test'}]}),/"'=SUM/));
