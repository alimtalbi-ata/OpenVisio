import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const main=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('interactive render uses cached topology',()=>assert.match(main,/renderGraph\(svg,interactiveVisibleGraph\(\),graphHandlers\)/));
test('cache invalidated on full paint',()=>assert.match(main,/function paint\(\)\{interactiveFrames\.cancel\(\);invalidateInteractiveGraph\(\)/));
test('cache is lazy and reused during pointer movement',()=>assert.match(main,/interactiveGraphCache\?\?\(interactiveGraphCache=visibleGraph\(\)\)/));
test('cached graph retains mutable node objects',()=>assert.match(main,/return \{\.\.\.state,nodes,edges:state\.edges\.filter/));
