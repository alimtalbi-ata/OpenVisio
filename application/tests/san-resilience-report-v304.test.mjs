import test from 'node:test';import assert from 'node:assert/strict';
import {buildFailureComparisonReport,failureComparisonCsv} from '../src/san-resilience-scenarios-v303.js';
const matrix={rows:[{priority:'P2',serverId:'host1',storageId:'array1',fabricA:2,fabricB:1,sharedTransitIds:['sw1']}]};
test('report includes baseline and both single-fabric failures',()=>{const r=buildFailureComparisonReport(matrix);assert.deepEqual(r.rows[0].cases.map(c=>c.remainingPaths),[3,1,2]);assert.equal(r.rows[0].sharedTransitIds[0],'sw1');});
test('report includes explicit topology-only disclaimer',()=>assert.match(buildFailureComparisonReport(matrix).disclaimer,/multipathing/));
test('CSV has three scenarios with fixed column counts',()=>{const lines=failureComparisonCsv(buildFailureComparisonReport(matrix)).trim().split('\r\n');assert.equal(lines.length,4);assert.ok(lines[2].includes('FABRIC_A_DOWN'));});
test('CSV prevents formula injection',()=>{const r=buildFailureComparisonReport({rows:[{...matrix.rows[0],serverId:'=CMD()'}]});assert.match(failureComparisonCsv(r),/"'=CMD\(\)"/);});
