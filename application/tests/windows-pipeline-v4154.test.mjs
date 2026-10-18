import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const pipeline = readFileSync(new URL('../windows/Invoke-Windows-Release-Pipeline.ps1', import.meta.url),'utf8');
const installer = readFileSync(new URL('../windows/Test-Installer-E2E.ps1', import.meta.url),'utf8');
test('v41.54 pipeline checks installer phase evidence',()=>{for(const x of ['install','assets','startup','uninstall','cleanup'])assert.ok(pipeline.includes(x));assert.match(pipeline,/installer-e2e-result\.json/)});
test('v41.54 startup evidence required for native and portable',()=>{assert.match(pipeline,/startup-native\.json/);assert.match(pipeline,/startup-portable\.json/);assert.match(pipeline,/startup -ne 'PASS'/)});
test('v41.54 installer writes overall status and error evidence',()=>{assert.match(installer,/status='NOT_RUN'/);assert.match(installer,/report\.error/);assert.match(installer,/report\.status/)});
