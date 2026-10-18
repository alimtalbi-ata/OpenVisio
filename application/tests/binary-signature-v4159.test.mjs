import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const script=readFileSync(new URL('../windows/Stage-Binaries.ps1',import.meta.url),'utf8');
test('signature status recorded for both staged binaries',()=>{assert.match(script,/Get-AuthenticodeSignature/);assert.match(script,/signatureStatus=\$sigStatus/);});
test('strict signature policy fails closed',()=>{assert.match(script,/RequireValid/);assert.match(script,/Signature Authenticode invalide/);});
test('signature checked before atomic publication',()=>{assert.ok(script.indexOf('Get-AuthenticodeSignature')<script.indexOf('Move-Item -LiteralPath $pending -Destination $out'));});
