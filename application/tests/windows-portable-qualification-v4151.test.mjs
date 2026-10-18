import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = p => readFileSync(new URL(p, import.meta.url), 'utf8');
test('qualification invokes independent portable artifact smoke', () => {
 const q = read('../windows/Qualify-Windows-Release.ps1');
 assert.match(q, /portable_artifact_smoke/);
 assert.match(q, /Test-Portable-Artifact\.ps1/);
 assert.match(q, /SkipPortableSmoke/);
});
test('portable verification checks PE header and manifest digest', () => {
 const p = read('../windows/Test-Portable-Artifact.ps1');
 for (const expected of ['Get-FileHash', 'release-manifest.json', 'magic[0]', 'magic[1]', 'bytes', 'filename']) assert.ok(p.includes(expected), expected);
});
test('release qualification retains incomplete state for skipped checks', () => {
 const q = read('../windows/Qualify-Windows-Release.ps1');
 assert.match(q, /'SKIPPED'/);
 assert.match(q, /status='PARTIAL'/);
 assert.match(q, /exit 2/);
});
