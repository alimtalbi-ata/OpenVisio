import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const s=readFileSync(new URL('../windows/Stage-Binaries.ps1',import.meta.url),'utf8');
test('both Windows outputs required before publication',()=>{assert.match(s,/foreach \(\$item in \$items\)/);assert.match(s,/Binaire absent/);assert.match(s,/Binaire trop petit/);});
test('staging is private until manifest written',()=>{assert.match(s,/binary\.pending/);assert.ok(s.indexOf("Join-Path $pending 'manifest.json'")<s.indexOf('Move-Item -LiteralPath $pending -Destination $out'));});
test('rollback restores previous binary directory',()=>{assert.match(s,/binary\.previous/);assert.match(s,/Move-Item -LiteralPath \$previous -Destination \$out/);});
