import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('JSON download never marks document as confirmed saved',()=>{
 const save=src.slice(src.indexOf("$('saveJsonBtn').addEventListener"),src.indexOf("\n});",src.indexOf("$('saveJsonBtn').addEventListener"))+4);
 assert.match(save,/exportPendingVerification=true/);
 assert.doesNotMatch(save,/savedFingerprint\s*=\s*documentFingerprint/);
});
test('Opening a validated document resets baseline',()=>{
 assert.match(src,/savedFingerprint=documentFingerprint\(\);exportPendingVerification=false;paint\(\);notify\("Diagramme JSON importé/);
});
test('Close guard remains active for unconfirmed export',()=>{
 assert.match(src,/window.addEventListener\('beforeunload'/);
 assert.match(src,/if\(!isDocumentDirty\(\)\)return/);
});
