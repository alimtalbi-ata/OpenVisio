import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = x => readFileSync(new URL(x, import.meta.url), 'utf8');
test('release version synchronized across npm .NET and Inno', () => {
 const version = JSON.parse(read('../package.json')).version;
 assert.match(version, /^\d+\.\d+\.0$/);
 assert.ok(read('../windows/native/OpenVisio.csproj').includes(`<Version>${version}</Version>`));
 assert.ok(read('../windows/installer/OpenVisio.iss').includes(`#define AppVersion "${version}"`));
 assert.ok(read('../windows/installer/OpenVisio.iss').includes(`OutputBaseFilename=OpenVisio-Setup-v${version.slice(0,-2)}-x64`));
});
test('installer wrapper delegates to single complete build', () => {
 assert.match(read('../Build-Windows-Installer.cmd'), /Build-OpenVisio-Windows\.cmd/);
 assert.doesNotMatch(read('../Build-Windows-Installer.cmd'), /ISCC\.exe/);
});
