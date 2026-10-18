import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const script=readFileSync(new URL('../windows/Test-Binary-Recovery-Scenarios.ps1',import.meta.url),'utf8');
test('recovery suite covers positive restoration',()=>assert.match(script,/valid-checkpoint-restored/));
test('recovery suite refuses overwrite of valid release',()=>assert.match(script,/valid-binary-blocks-restore/));
test('recovery fixtures are explicitly synthetic',()=>assert.match(script,/Synthetic MZ fixtures/));
