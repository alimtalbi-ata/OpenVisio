import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const pipeline=readFileSync(new URL('../windows/Invoke-Windows-Release-Pipeline.ps1',import.meta.url),'utf8');
test('pipeline report filename derives from current package version',()=>{assert.match(pipeline,/pipeline-v' \+ \$version \+ '\.json/);assert.doesNotMatch(pipeline,/pipeline-v41\.54\.json/)});
test('pipeline validates both staged binary hashes',()=>{assert.match(pipeline,/binary\/manifest\.json/);assert.match(pipeline,/@\(\$m\.artifacts\)\.Count -ne 2/);assert.match(pipeline,/Artifact hash mismatch/)});
