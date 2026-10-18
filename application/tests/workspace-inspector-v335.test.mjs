import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const js=readFileSync(new URL('../src/workspace-inspector-v335.js',import.meta.url),'utf8');
test('v33.5 inspector filter controls are accessible',()=>{for(const id of ['inspectorFilter','inspectorFieldSearch','inspectorFieldCount'])assert.ok(html.includes(`id="${id}"`));});
test('v33.5 preserves all properties and filters without removing nodes',()=>{assert.match(js,/field.hidden=/);assert.doesNotMatch(js,/field.remove\(/);assert.match(js,/mode.value==='all'/);});
test('v33.5 filter updates after canvas repaint',()=>assert.match(js,/openvisio:canvas-painted/));
test('v33.5 keeps inspector fields interactive',()=>assert.match(js,/querySelectorAll\('\.field'\)/));
