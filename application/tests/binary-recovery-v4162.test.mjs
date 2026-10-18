import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../windows/Inspect-Binary-Recovery.ps1',import.meta.url),'utf8');
test('recovery inspection defaults to non-mutating mode',()=>{assert.match(src,/action = 'INSPECT_ONLY'/);assert.match(src,/if \(\$RestorePrevious\)/)});
test('restoration requires explicit confirmation and refuses valid current release',()=>{assert.match(src,/-ConfirmRecovery obligatoire/);assert.match(src,/binary actuel valide/)});
test('restoration blocks pending or invalid previous release',()=>{assert.match(src,/binary\.pending existe/);assert.match(src,/binary\.previous invalide/)});
test('recovery verifies two artifact hashes and writes JSON evidence',()=>{assert.match(src,/Count -ne 2/);assert.match(src,/Get-FileHash/);assert.match(src,/binary-recovery-assessment\.json/)});
