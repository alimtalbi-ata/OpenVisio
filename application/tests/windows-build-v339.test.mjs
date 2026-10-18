import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const build=readFileSync('Build-OpenVisio-Windows.cmd','utf8');
const iss=readFileSync('windows/installer/OpenVisio.iss','utf8');
test('v33.9 installer path consistent in build and Inno Setup',()=>{const v=JSON.parse(readFileSync('package.json','utf8')).version.replace(/\.0$/,'');const file=`OpenVisio-Setup-v${v}-x64`;assert.ok(iss.includes(`OutputBaseFilename=${file}`));assert.ok(build.includes(`${file}.exe`));});
test('clean publish prevents stale application binaries',()=>{assert.match(build,/rmdir \/s \/q "dist\\windows-x64"/);});
test('WebView2 prerequisite checks signature',()=>{assert.match(build,/Get-AuthenticodeSignature/);assert.match(iss,/HasWebView2/);});
