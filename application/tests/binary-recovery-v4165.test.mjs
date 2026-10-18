import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const s=readFileSync(new URL('../windows/Test-Binary-Recovery-Scenarios.ps1',import.meta.url),'utf8');
test('recovery runner persists report outside disposable fixture',()=>{assert.match(s,/ReportPath/);assert.match(s,/Set-Content -LiteralPath \$ReportPath/)});
test('recovery runner reports explicit FAIL and nonzero exit',()=>{assert.match(s,/status=\$\(if \(\$failed\)/);assert.match(s,/if \(\$failed\) \{ exit 1 \}/)});
test('recovery runner cleans only temporary fixture',()=>{assert.match(s,/GetTempPath/);assert.match(s,/Remove-Item -LiteralPath \$root -Recurse/)});
