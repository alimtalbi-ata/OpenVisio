import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = p => readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('inspector has SAN shortcut and reset actions',()=>{for(const id of ['inspectorSanFields','inspectorClearFilter']) assert.match(read('index.html'),new RegExp(`id="${id}"`));});
test('search overrides essential mode so hidden properties can be found',()=>assert.match(read('src/workspace-inspector-v335.js'),/Boolean\(query\)\|\|mode.value==='all'/));
test('SAN shortcut searches SAN properties and supports reset',()=>{assert.match(read('src/workspace-inspector-v386.js'),/search.value = '@san'/);assert.match(read('src/workspace-inspector-v335.js'),/powerdomain\|controller\|failuredomain/);assert.match(read('src/workspace-inspector-v386.js'),/mode.value = 'essential'/);});
