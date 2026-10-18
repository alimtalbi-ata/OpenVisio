import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
const preview=main.slice(main.indexOf(' const showBatchConflictPreview='),main.indexOf(' const checkboxes=new Map()'));
test('v27.3 compare preview draws before and after paths',()=>{assert.match(preview,/visibleRoutes\.get/);assert.match(preview,/routeEdge\(a,b/);assert.match(preview,/#16a34a/);assert.match(preview,/#e11d48/);});
test('v27.3 compare preview does not commit or mutate',()=>{assert.doesNotMatch(preview,/saveUndo\(|commitRouteBatch\(|\.offset\s*=/);});
test('v27.3 group exposes compare action and gain',()=>{assert.match(main,/Comparer avant \/ après/);assert.match(main,/Gain estimé du groupe/);});
test('v27.3 compare uses existing preview overlay',()=>{assert.match(preview,/clearPreview\(\)/);assert.match(preview,/routePreviewOverlay/);});
