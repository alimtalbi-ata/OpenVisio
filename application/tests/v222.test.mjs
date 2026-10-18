import test from 'node:test';
import assert from 'node:assert/strict';
import {diagnoseRouteTopology} from '../src/routing.js';
const route=(...points)=>({points:points.map(([x,y])=>({x,y}))});
test('diagnostic detects strict interior crossing',()=>{const r=new Map([['a',route([0,5],[20,5])],['b',route([10,0],[10,10])]]);assert.equal(diagnoseRouteTopology(r).crossingPairs,1);});
test('diagnostic counts overlapping segments',()=>{const r=new Map([['a',route([0,0],[20,0])],['b',route([10,0],[30,0])]]);assert.equal(diagnoseRouteTopology(r).overlappingSegmentPairs,1);});
test('diagnostic counts obstacle collisions and does not mutate',()=>{const r=new Map([['a',route([0,0],[20,0])]]);const before=JSON.stringify([...r]);assert.equal(diagnoseRouteTopology(r,[{x:5,y:-2,w:5,h:4}]).obstacleCollisions,1);assert.equal(JSON.stringify([...r]),before);});
test('diagnostic truncates and skips quadratic pairs',()=>{const r=new Map(Array.from({length:100},(_,i)=>[String(i),route([0,i],[100,i])]));const d=diagnoseRouteTopology(r,[],{maxSegments:30});assert.equal(d.truncated,true);assert.equal(d.pairAnalysisComplete,false);assert.equal(d.crossingPairs,null);});
test('diagnostic ignores invalid paths safely',()=>{const r=new Map([['bad',{points:[{x:0,y:0},{x:NaN,y:1}]}]]);assert.equal(diagnoseRouteTopology(r).invalidRoutes,1);});
