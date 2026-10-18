import test from 'node:test';import assert from 'node:assert/strict';
import {sparklinePoints,visualAuditModel} from '../src/san-visual-audit.js';
test('sparkline vide',()=>assert.equal(sparklinePoints([]),''));
test('sparkline valeur unique',()=>assert.equal(sparklinePoints([50]),'300,50'));
test('sparkline bornes',()=>assert.equal(sparklinePoints([-1,101],100,100),'0,100 100,0'));
test('modèle vide',()=>{const m=visualAuditModel([]);assert.equal(m.changes.length,0);assert.equal(m.entries.length,0)});
test('filtre fabric vide',()=>assert.deepEqual(visualAuditModel([],{fabric:'A'}).entries,[]));
