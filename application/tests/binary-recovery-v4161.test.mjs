import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const script=readFileSync(new URL('../windows/Stage-Binaries.ps1',import.meta.url),'utf8');
test('stale staging and backup block potentially destructive publication',()=>{
 assert.match(script,/binary\.pending existe/);
 assert.match(script,/binary\.previous existante/);
});
test('failure evidence is saved outside the staging directory',()=>{
 assert.match(script,/binary-publication-failure\.json/);
});
test('previous release retained as recovery checkpoint',()=>{
 assert.match(script,/Preserve binary\.previous as a recovery checkpoint/);
 assert.doesNotMatch(script,/Remove-Item -LiteralPath \$previous -Recurse -Force/);
});
