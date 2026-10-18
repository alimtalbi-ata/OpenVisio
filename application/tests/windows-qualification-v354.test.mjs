import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=(p)=>readFileSync(p,'utf8');
test('v35.4 qualification orchestrator writes JSON report',()=>{const s=read('windows/Qualify-Windows-Release.ps1');assert.match(s,/qualification-summary\.json/);assert.match(s,/ConvertTo-Json/);});
test('v35.4 qualification invokes preflight and HTTP smoke',()=>{const s=read('windows/Qualify-Windows-Release.ps1');assert.match(s,/Preflight-Windows\.ps1/);assert.match(s,/Validate-OpenVisio-Windows\.ps1/);});
test('v35.4 qualification invokes installer E2E',()=>assert.match(read('windows/Qualify-Windows-Release.ps1'),/Test-Installer-E2E\.ps1/));
test('v35.4 installer E2E checks elevation',()=>assert.match(read('windows/Test-Installer-E2E.ps1'),/WindowsBuiltInRole/));
test('v35.4 launcher propagates errorlevel',()=>assert.match(read('Qualify-OpenVisio-Windows.cmd'),/exit \/b %ERRORLEVEL%/));
