import test from 'node:test';import assert from 'node:assert/strict';import {classifySpofRisk,spofRiskCsv} from '../src/san-spof-priority.js';
test('P1 avec perte applicative',()=>assert.equal(classifySpofRisk({loss:1,applications:1}).level,'P1'));
test('P2 pour une paire perdue sans application',()=>assert.equal(classifySpofRisk({loss:1}).level,'P2'));
test('P3 pour dégradation sans perte',()=>assert.equal(classifySpofRisk({degraded:2}).level,'P3'));
test('P4 pour absence de preuve',()=>assert.equal(classifySpofRisk({loss:NaN,degraded:-1}).level,'P4'));
test('CSV neutralise injection de formule',()=>assert.match(spofRiskCsv({rows:[{priority:'P1',kind:'fabric',id:'=1+1',label:'test',loss:1,degraded:0,applications:0,reason:'x',recommendation:'y'}]}),/"'=1\+1"/));
