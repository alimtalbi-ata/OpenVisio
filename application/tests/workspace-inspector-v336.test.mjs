import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const js=readFileSync(new URL('../src/workspace-inspector-v336.js',import.meta.url),'utf8');
test('v33.6 toggle exposes correct aria controls',()=>{assert.match(html,/id="inspectorFieldsToggle"/);assert.match(html,/aria-controls="inspectorContent"/);});
test('v33.6 collapses without destroying editor fields',()=>{assert.match(js,/content.hidden=!expanded/);assert.doesNotMatch(js,/removeChild|\.remove\(/);});
test('v33.6 remembers collapse preference safely',()=>{assert.match(js,/localStorage\.setItem/);assert.match(js,/try\{/);});
test('v33.6 inspector quick access expands properties',()=>assert.match(js,/inspectSelectionBtn/));
