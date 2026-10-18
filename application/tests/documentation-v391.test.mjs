import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {join} from 'node:path';
const root=new URL('../',import.meta.url);const read=p=>readFileSync(new URL(p,root),'utf8');
test('v39.1 includes a versioned manifest generator',()=>assert.match(read('scripts/generate-release-manifest.mjs'),/createHash/));
test('v39.1 verifies required documentation and path safety',()=>{const s=read('scripts/verify-release-docs.mjs');assert.match(s,/required=/);assert.match(s,/Chemin interdit/)});
test('v39.1 includes Word and PDF documentation',()=>{const s=read('documentation/NOTES-DE-VERSION-V39.1.md');assert.match(s,/SHA256/)});
