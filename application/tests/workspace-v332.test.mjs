import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');const js=fs.readFileSync(new URL('../src/workspace-modes-v332.js',import.meta.url),'utf8');const css=fs.readFileSync(new URL('../styles/workspace-v332.css',import.meta.url),'utf8');
test('v33.2 includes workspace mode assets',()=>{assert.match(html,/workspace-modes-v332\.js/);assert.match(html,/workspace-v332\.css/)});
test('v33.2 keeps three named modes and accessible pressed state',()=>{for(const name of ['edition','san','advanced'])assert.match(js,new RegExp(name+':'));assert.match(js,/aria-pressed/)});
test('v33.2 persists chosen mode with guarded localStorage',()=>{assert.match(js,/localStorage\.setItem/);assert.match(js,/try\{/)});
test('v33.2 hides analytical panels only in edition mode',()=>{assert.match(css,/data-ov-mode="edition"/);assert.match(css,/display:none/);assert.match(css,/data-ov-mode="san"/)});
