import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const recovery=readFileSync(new URL('../windows/Inspect-Binary-Recovery.ps1',import.meta.url),'utf8');
const scenarios=readFileSync(new URL('../windows/Test-Binary-Recovery-Scenarios.ps1',import.meta.url),'utf8');
test('recovery rejects Windows filename aliases case insensitively',()=>assert.match(recovery,/Sort-Object -Unique/));
test('recovery rejects unsafe executable names',()=>assert.match(recovery,/A-Za-z0-9\._-/));
test('recovery rejects reparse-point artifacts',()=>assert.match(recovery,/FileAttributes\]::ReparsePoint/));
test('Windows scenario runner uses isolated temporary directory and cleanup',()=>{assert.match(scenarios,/GetTempPath/);assert.match(scenarios,/Remove-Item -LiteralPath \$root -Recurse/)});
