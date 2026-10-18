import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const q=readFileSync('windows/Qualify-Windows-Release.ps1','utf8');
test('graphic qualification is explicit opt-in',()=>assert.match(q,/\[switch\]\$RunGraphicSmoke/));
test('graphic qualification reuses browser runner',()=>assert.match(q,/Run-Graphic-Qualification\.ps1/));
test('graphic qualification verifies evidence',()=>{assert.match(q,/browser-report\.json/);assert.match(q,/openvisio-ui-real\.png/)});
test('graphic qualification marks skipped partial',()=>assert.match(q,/name='graphic_browser_smoke';status='SKIPPED'/));
test('graphic cmd wrapper exists',()=>assert.ok(existsSync('Qualify-OpenVisio-Windows-Graphic.cmd')));
