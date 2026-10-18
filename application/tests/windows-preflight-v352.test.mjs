import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
test('preflight version derives from package metadata', () => {
 const source=read('windows/Preflight-Windows.ps1');
 assert.match(source,/\$shortVersion = \$version/);
 assert.doesNotMatch(source,/34\\\.3/);
});
test('Windows shell version agrees with package metadata', () => {
 const version=JSON.parse(read('package.json')).version.replace(/\.0$/,'');
 assert.ok(read('windows/native/Program.cs').includes('OpenVisio '+version));
});
test('build and installer agree on expected setup filename', () => {
 const version=JSON.parse(read('package.json')).version.replace(/\.0$/,'');
 const expected=`OpenVisio-Setup-v${version}-x64`;
 assert.ok(read('Build-OpenVisio-Windows.cmd').includes(expected+'.exe'));
 assert.ok(read('windows/installer/OpenVisio.iss').includes('OutputBaseFilename='+expected));
});
