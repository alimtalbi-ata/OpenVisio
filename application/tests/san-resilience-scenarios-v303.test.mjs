import test from 'node:test';import assert from 'node:assert/strict';
import {compareFabricFailures,scenarioFocusIds,formatFabricComparison} from '../src/san-resilience-scenarios-v303.js';
test('A/B independent paths are degraded by one fabric loss',()=>{const r=compareFabricFailures({fabricA:2,fabricB:3});assert.equal(r.cases[1].remainingPaths,3);assert.equal(r.cases[2].remainingPaths,2);assert.equal(r.cases[1].status,'DEGRADED');});
test('single fabric dependency is lost when its fabric fails',()=>{const r=compareFabricFailures({fabricA:1,fabricB:0});assert.equal(r.cases[1].status,'LOSS');assert.equal(r.cases[2].remainingPaths,1);});
test('common transit is deduplicated and warned',()=>{const r=compareFabricFailures({fabricA:1,fabricB:1,sharedTransitIds:['sw1','sw1','sw2']});assert.deepEqual(r.sharedTransitIds,['sw1','sw2']);assert.match(formatFabricComparison(r),/communes/);});
test('focus IDs exclude invalid and duplicates',()=>assert.deepEqual(scenarioFocusIds({serverId:'srv',storageId:'srv',sharedTransitIds:['sw','',null]}),['srv','sw']));
test('invalid counts never create negative paths',()=>{const r=compareFabricFailures({fabricA:-2,fabricB:'oops'});assert.equal(r.baselinePaths,0);});
