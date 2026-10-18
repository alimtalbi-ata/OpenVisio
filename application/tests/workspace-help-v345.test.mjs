import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const html=readFileSync('index.html','utf8');
const js=readFileSync('src/workspace-help-v345.js','utf8');
test('v34.5 help control is reachable',()=>assert.match(html,/id="workspaceHelpBtn"/));
test('v34.5 help module loaded',()=>assert.match(html,/workspace-help-v345\.js/));
test('v34.5 help is keyboard accessible',()=>assert.match(js,/event\.key === 'F1'/));
test('v34.5 help uses accessible modal',()=>assert.match(js,/showModal\(\)/));
