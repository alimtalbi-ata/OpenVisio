import test from 'node:test';
import assert from 'node:assert/strict';
import {countRouteCrossings,reduceFanOutCrossings} from '../src/routing.js';
const route=(points)=>({points,orthogonalFanOut:true});
test('incremental candidate comparison preserves global crossing score differences',()=>{
 const a=route([{x:0,y:10},{x:30,y:10}]);
 const b=route([{x:10,y:0},{x:10,y:30}]);
 const c=route([{x:20,y:0},{x:20,y:30}]);
 const moved=route([{x:0,y:40},{x:30,y:40}]);
 const globalBefore=countRouteCrossings([a,b,c]);
 const globalAfter=countRouteCrossings([moved,b,c]);
 const localBefore=countRouteCrossings([a,b])+countRouteCrossings([a,c]);
 const localAfter=countRouteCrossings([moved,b])+countRouteCrossings([moved,c]);
 assert.equal(globalAfter-globalBefore,localAfter-localBefore);
});
test('crossing reducer retains its public input validation',()=>{
 assert.throws(()=>reduceFanOutCrossings([],new Map(),[],{maxEdges:0}),/Invalid/);
});
