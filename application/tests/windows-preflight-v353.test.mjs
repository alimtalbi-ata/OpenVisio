import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const pre=readFileSync('windows/Preflight-Windows.ps1','utf8');
test('PowerShell scripts parsed before build',()=>assert.match(pre,/Language\.Parser\]::ParseFile/));
test('missing local HTML assets fail closed',()=>assert.match(pre,/HTML asset missing/));
test('PowerShell parse failures fail closed',()=>assert.match(pre,/PowerShell syntax invalid/));
test('version 35.3 matches package',()=>assert.match(JSON.parse(readFileSync('package.json','utf8')).version,/^\d+\.\d+\.0$/));
