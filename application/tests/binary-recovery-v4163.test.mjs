import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../windows/Inspect-Binary-Recovery.ps1',import.meta.url),'utf8');
test('recovery rejects duplicate filenames in manifest',()=>assert.match(src,/Sort-Object -Unique/));
test('recovery verifies Windows MZ magic bytes',()=>assert.match(src,/ReadByte\(\) -ne 77.*ReadByte\(\) -ne 90/));
test('recovery rechecks restored release and rolls back on failure',()=>{assert.match(src,/if \(!\(Test-Release \$binary\)\)/);assert.match(src,/Move-Item -LiteralPath \$binary -Destination \$previous/)});
