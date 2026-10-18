import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
const focus=main.slice(main.indexOf(' const focusBatchConflictGroup='),main.indexOf(' const checkboxes=new Map()'));
test('v27.4 navigation locates group using actual rendered edge geometry',()=>{assert.match(focus,/data-edge-id/);assert.match(focus,/getBoundingClientRect/);assert.match(focus,/edgeViewportTarget/);});
test('v27.4 navigation does not mutate document or history',()=>{assert.doesNotMatch(focus,/saveUndo\(|commitRouteBatch\(|state\.edges\s*=/);});
test('v27.4 group has locate and previous next navigation',()=>{assert.match(main,/Cadrer le groupe/);assert.match(main,/Groupe précédent/);assert.match(main,/Groupe suivant/);});
test('v27.4 navigation retains non destructive before-after preview',()=>{assert.match(main,/showBatchConflictPreview\(target.edgeIds,\{compare:true\}\)/);});
