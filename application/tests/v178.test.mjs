import test from 'node:test';
import assert from 'node:assert/strict';
import {createInteractionMetrics} from '../src/interaction-metrics.js';
test('empty metrics are zero',()=>assert.equal(createInteractionMetrics().snapshot().count,0));
test('rolling window discards oldest sample',()=>{const m=createInteractionMetrics({capacity:2});[2,4,8].forEach(x=>m.record(x));assert.equal(m.snapshot().meanMs,6);});
test('percentiles and frame budget',()=>{const m=createInteractionMetrics();[2,4,20,30].forEach(x=>m.record(x));assert.equal(m.snapshot().p95Ms,30);assert.equal(m.snapshot().over16ms,2);});
test('invalid samples ignored',()=>{const m=createInteractionMetrics();assert.equal(m.record(-1),false);assert.equal(m.record(Infinity),false);assert.equal(m.snapshot().count,0);});
test('reset clears measurements',()=>{const m=createInteractionMetrics();m.record(5);m.reset();assert.equal(m.snapshot().count,0);});
test('invalid capacity rejected',()=>assert.throws(()=>createInteractionMetrics({capacity:0}),RangeError));
