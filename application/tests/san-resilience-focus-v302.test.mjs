import test from 'node:test';import assert from 'node:assert/strict';
import {normalizeFocusIds,applyResilienceFocus} from '../src/san-resilience-focus-v302.js';
import {resilienceFocusIds} from '../src/san-resilience-v300-ui.js';
test('stable focus ids deduplicated',()=>assert.deepEqual(resilienceFocusIds({serverId:'h1',storageId:'s1',sharedTransitIds:['h1','sw1']}),['h1','s1','sw1']));
test('invalid focus ids rejected',()=>assert.deepEqual(normalizeFocusIds(['a',null,'',42,'a']),['a']));
test('missing DOM is safe',()=>assert.equal(applyResilienceFocus(null,['a']),0));
