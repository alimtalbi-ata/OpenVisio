import test from 'node:test';
import assert from 'node:assert/strict';
import {createFrameScheduler} from '../src/frame-scheduler.js';
function harness(){let id=0;const tasks=new Map();let draws=0;const scheduler=createFrameScheduler(()=>draws++,{request:fn=>{tasks.set(++id,fn);return id;},cancel:id=>tasks.delete(id)});return {scheduler,tasks,get draws(){return draws;}};}
test('coalesces multiple requests into one frame',()=>{const h=harness();assert.equal(h.scheduler.schedule(),true);assert.equal(h.scheduler.schedule(),false);assert.equal(h.tasks.size,1);[...h.tasks.values()][0]();assert.equal(h.draws,1);});
test('flush cancels queued callback and draws immediately',()=>{const h=harness();h.scheduler.schedule();assert.equal(h.scheduler.flush(),true);assert.equal(h.tasks.size,0);assert.equal(h.draws,1);assert.equal(h.scheduler.flush(),false);});
test('cancel drops pending redraw',()=>{const h=harness();h.scheduler.schedule();assert.equal(h.scheduler.cancel(),true);assert.equal(h.draws,0);assert.equal(h.tasks.size,0);});
test('dispose prevents future redraw',()=>{const h=harness();h.scheduler.schedule();h.scheduler.dispose();assert.equal(h.scheduler.schedule(),false);assert.equal(h.tasks.size,0);});
test('schedule works again after completed frame',()=>{const h=harness();h.scheduler.schedule();[...h.tasks.values()][0]();assert.equal(h.scheduler.schedule(),true);});
