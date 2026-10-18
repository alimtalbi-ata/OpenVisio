import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../src/workspace-inspector-v387.js',import.meta.url),'utf8');
test('categories validated before persisting',()=>{assert.match(source,/allowedCategories\.has\(category\)/);assert.match(source,/localStorage\.setItem\(storageKey, category\)/)});
test('reset clears query and returns to essential properties',()=>{assert.match(source,/inspectorClearFilter[\s\S]*search\.value = ''/);assert.match(source,/mode\.value = 'essential'/)});
test('SAN shortcut reveals complete SAN fields',()=>{assert.match(source,/inspectorSanFields[\s\S]*mode\.value = 'all'/)});
