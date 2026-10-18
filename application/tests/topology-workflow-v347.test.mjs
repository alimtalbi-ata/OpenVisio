import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {matchSanSections,installSanWorkflow,SAN_SECTIONS} from '../src/topology-workflow-v347.js';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
test('34.7 workflow is linked',()=>assert.match(html,/src\/topology-workflow-v347\.js/));
test('34.7 filter finds zoning regardless of case',()=>assert.deepEqual(matchSanSections('ZONING').map(x=>x[0]),['Zoning']));
test('34.7 empty filter exposes all sections',()=>assert.equal(matchSanSections('').length,SAN_SECTIONS.length));
test('34.7 missing dialog is safe',()=>assert.equal(installSanWorkflow({getElementById:()=>null}),false));
