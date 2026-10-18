import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const portable=readFileSync(new URL('../windows/Build-Portable-Windows.ps1',import.meta.url),'utf8');
const csproj=readFileSync(new URL('../windows/native/OpenVisio.csproj',import.meta.url),'utf8');
test('portable artifact filename is derived from csproj release version',()=>{assert.match(portable,/Get-Content -LiteralPath \$project -Raw/);assert.match(portable,/OpenVisio-v\{0\}-Windows-x64-Portable\.exe/);assert.doesNotMatch(portable,/OpenVisio-v36\.8-Windows-x64-Portable\.exe/)});
test('assembly version matches release metadata',()=>{const v=JSON.parse(readFileSync(new URL('../package.json',import.meta.url),'utf8')).version;assert.ok(csproj.includes(`<Version>${v}</Version>`));});
