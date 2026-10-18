import test from 'node:test';
import assert from 'node:assert/strict';
import {spofSelectors,highlightSpofTarget,clearSpofHighlight,filterRiskRows} from '../src/san-spof-panel-v295.js';
test('stable node selector',()=>assert.deepEqual(spofSelectors({kind:'node',id:'h1'}),[{attr:'data-object-id',id:'h1'}]));
test('stable edge selector',()=>assert.deepEqual(spofSelectors({kind:'edge',id:'e1'}),[{attr:'data-connection-id',id:'e1'}]));
test('fabric requires dedicated mapping',()=>assert.deepEqual(spofSelectors({kind:'fabric',id:'A'}),[]));
test('missing svg safely returns zero',()=>assert.equal(highlightSpofTarget({querySelector:()=>null},{kind:'node',id:'x'}),0));
test('clear is idempotent',()=>{clearSpofHighlight();clearSpofHighlight();});
