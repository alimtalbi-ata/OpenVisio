import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const read = (p) => readFileSync(new URL('../'+p, import.meta.url),'utf8');
test('CI uses the single build entry point',()=>assert.match(read('.github/workflows/windows-release.yml'),/call Build-OpenVisio-Windows\.cmd/));
test('CI does not invoke legacy installer path',()=>assert.doesNotMatch(read('.github/workflows/windows-release.yml'),/choco install innosetup/));
test('CI checks bundled WebView2 prerequisite',()=>assert.match(read('.github/workflows/windows-release.yml'),/Get-AuthenticodeSignature \$webview/));
test('CI uploads exact versioned installer',()=>assert.match(read('.github/workflows/windows-release.yml'),/dist\/installer\/OpenVisio-Setup-v(?:34\.[0-9]|(?:35\.[0-9]|(?:36\.[0-9]|(?:(?:37\.[0-9]|(?:38\.[0-9]|39\.[0-9]|(?:40\.[0-9]|41\.0)))|(?:38\.[0-9]|39\.[0-9]|(?:40\.[0-9]|41\.0))))))-x64\.exe/));
test('single builder checks native resources',()=>assert.match(read('Build-OpenVisio-Windows.cmd'),/wwwroot\\src\\main\.js/));
