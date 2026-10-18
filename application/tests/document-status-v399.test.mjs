import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('indicateur non enregistré fondé sur empreinte documentaire',()=>{assert.match(source,/function documentFingerprint\(\)/);assert.match(source,/function isDocumentDirty\(\)/);assert.match(source,/documentSaveStatus/);});
test('alerte avant fermeture et avant remplacement conditionnées par modifications',()=>{assert.match(source,/beforeunload/);assert.match(source,/if\(!isDocumentDirty\(\)\)return/);assert.match(source,/if\(isDocumentDirty\(\) && !confirm/);});
test('export non confirmé et ouverture réinitialisant le témoin',()=>{assert.match(source,/exportPendingVerification=true;refreshDocumentStatus\(\)/);assert.match(source,/savedFingerprint=documentFingerprint\(\);exportPendingVerification=false;paint\(\);notify\("Diagramme JSON importé/);});
