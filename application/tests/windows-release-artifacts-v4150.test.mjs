import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
test('release manifest requires both installer and portable artifacts',()=>{
 const m=read('windows/Write-Release-Manifest.ps1');
 assert.match(m,/Missing installer/); assert.match(m,/Missing portable/);
 assert.match(m,/kind='installer'/); assert.match(m,/kind='portable'/);
 assert.match(m,/Get-FileHash/); assert.match(m,/0x4d/); assert.match(m,/0x5a/);
});
test('portable build rejects stale and undersized output',()=>{
 const s=read('windows/Build-Portable-Windows.ps1');
 assert.match(s,/Remove-Item -LiteralPath \$target/);
 assert.match(s,/Portable anormalement petit/);
});
