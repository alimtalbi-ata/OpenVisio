import test from 'node:test';import assert from 'node:assert/strict';import {filterResilience,resilienceSummary} from '../src/san-resilience-v300-ui.js';
test('filtre P1',()=>assert.equal(filterResilience({rows:[{priority:'P1'},{priority:'P2'}]},'P1').length,1));
test('filtre global',()=>assert.equal(filterResilience({rows:[{priority:'P1'},{priority:'P2'}]}).length,2));
test('rapport absent',()=>assert.deepEqual(filterResilience(null),[]));
test('synthèse stable',()=>assert.deepEqual(resilienceSummary([{priority:'P1'},{priority:'P1'},{priority:'P4'}]),{P1:2,P2:0,P3:0,P4:1}));
