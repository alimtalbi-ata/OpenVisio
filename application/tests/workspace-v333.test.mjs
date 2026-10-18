import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const js=readFileSync(new URL('../src/workspace-quick-v333.js',import.meta.url),'utf8');
test('v33.3 contextual actions included',()=>assert.match(html,/workspace-quick-v333\.js/));
test('v33.3 keyboard accessible actions',()=>assert.match(js,/type='button'/));
test('v33.3 SAN actions reference existing IDs',()=>{for(const id of ['sanSpofPanel','sanImportCorrelationPanel'])assert.ok(html.includes(`id="${id}"`));});
