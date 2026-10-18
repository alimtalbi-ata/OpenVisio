import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const script=readFileSync(new URL('../windows/Test-Windows-Startup.ps1',import.meta.url),'utf8');
test('v41.52 startup smoke supports portable and native executables',()=>{assert.match(script,/ValidateSet\('Portable','Native'\)/);assert.match(script,/Start-Process -FilePath \$exe/)});
test('v41.52 startup smoke captures failure and closes process',()=>{assert.match(script,/startup = 'FAIL'/);assert.match(script,/Stop-Process -Id \$process.Id/);assert.match(script,/finally/)});
test('v41.52 startup smoke persists JSON report and checks executable header',()=>{assert.match(script,/ConvertTo-Json/);assert.match(script,/Invalid PE\/MZ header/);assert.match(script,/startup-\$\(\$Mode.ToLowerInvariant\(\)\)\.json/)});
