import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('v27.2 preview overlay uses existing route geometry and no write',()=>{const start=main.indexOf('const showBatchConflictPreview=');const end=main.indexOf('const checkboxes=new Map()',start);const fragment=main.slice(start,end);assert.match(fragment,/visibleRoutes\.get/);assert.match(fragment,/routePreviewOverlay/);assert.doesNotMatch(fragment,/saveUndo\(|commitRouteBatch\(|\.offset\s*=/);});
test('v27.2 group controls expose highlight, select and deselect',()=>{for(const label of ['Surligner ce groupe','Sélectionner les liens du groupe','Désélectionner ce groupe'])assert.ok(main.includes(label));});
test('v27.2 group selection recalculates conflicts',()=>{assert.match(main,/cb\.checked=true;\}refreshConflictPanel\(\)/);assert.match(main,/cb\.checked=false;\}refreshConflictPanel\(\)/);});
