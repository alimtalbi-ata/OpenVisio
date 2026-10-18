import test from 'node:test';import assert from 'node:assert/strict';import {formatRedundancy,mountRedundancyPanel} from '../src/san-redundancy-panel-v364.js';
test('counts healthy and degraded SAN paths',()=>assert.deepEqual(formatRedundancy({paths:[{fabricA:true,fabricB:true},{fabricA:true,fabricB:false}],issues:[{severity:'error'},{severity:'warning'}]}),{paths:2,healthy:1,errors:1,warnings:1}));
test('handles empty result',()=>assert.deepEqual(formatRedundancy(null),{paths:0,healthy:0,errors:0,warnings:0}));
test('no dialog means no panel',()=>assert.equal(mountRedundancyPanel({getElementById:()=>null}),false));
