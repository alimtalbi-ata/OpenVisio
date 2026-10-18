import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildRouteClearanceView,renderRouteClearancePanel} from '../src/route-clearance-view.js';
const diagnostics={edges:[{edgeId:'A',errors:1,reviews:0,issues:[]},{edgeId:'B',errors:0,reviews:1,issues:[]}]};
test('classement des anomalies stable',()=>assert.deepEqual(buildRouteClearanceView(diagnostics).items.map(x=>x.severity),['error','review']));
test('filtre invalide rejeté',()=>assert.throws(()=>renderRouteClearancePanel({replaceChildren(){}},diagnostics,{filter:'unknown'}),RangeError));
test('filtre de gravité raccordé à UI',()=>{const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');assert.match(html,/id="routeQualityFilter"/);assert.match(main,/filter:\$\('routeQualityFilter'\)/);assert.match(main,/addEventListener\('change',refreshRouteQualityPanel\)/)});
