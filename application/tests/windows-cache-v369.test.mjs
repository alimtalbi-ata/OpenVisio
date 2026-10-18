import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const source = fs.readFileSync(new URL('../windows/native/Program.cs', import.meta.url), 'utf8');
test('cache reuse hashes each extracted file', () => { assert.match(source, /SHA256.HashData\(expectedStream\)/); assert.match(source, /SHA256.HashData\(actualStream\)/); });
test('cache integrity comparison is constant-time', () => assert.match(source, /CryptographicOperations.FixedTimeEquals/));
test('cache integrity rejects changed file lengths', () => assert.match(source, /entry.Length != actualStream.Length/));
test('cache paths remain confined to cache directory', () => assert.match(source, /candidate.StartsWith\(Path.GetFullPath\(cache\)/));
