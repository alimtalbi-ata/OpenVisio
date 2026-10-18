import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {installTopologyNavigator} from '../src/topology-navigator-v346.js';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
test('navigator is wired to application',()=>assert.match(html,/src\/topology-navigator-v346\.js/));
test('navigation targets are present',()=>{for(const id of ['topologyDiffDialog','topologyZoningSummary','topologyRelationsSummary','topologyChainSection'])assert.ok(html.includes(`id="${id}"`),id)});
test('navigator safely declines missing dialog',()=>assert.equal(installTopologyNavigator({getElementById:()=>null}),false));
