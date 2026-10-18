import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const py=fs.readFileSync('tests/browser-functional-v358.py','utf8');const ps=fs.readFileSync('windows/Qualify-Windows-Release.ps1','utf8');
test('JSON download is verified',()=>assert.match(py,/expect_download[\s\S]*saveJsonBtn/));
test('SVG download is verified',()=>assert.match(py,/expect_download[\s\S]*exportBtn/));
test('JSON is reopened through input',()=>assert.match(py,/openJsonInput.*set_input_files/));
test('qualification uses current functional scenario',()=>assert.match(ps,/browser-functional-v361\.py/));
