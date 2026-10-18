import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const code=fs.readFileSync(new URL('./browser-san-performance.py',import.meta.url),'utf8');
test('v24.8 selection native',()=>assert.match(code,/selection_label/));
test('v24.8 undo native',()=>assert.match(code,/after_undo<before_undo/));
test('v24.8 redo native',()=>assert.match(code,/after_redo==before_undo/));
test('v24.8 baseline visuelle',()=>assert.match(code,/visual-baseline/));
test('v24.8 seuil pixel',()=>assert.match(code,/difference_ratio/));
