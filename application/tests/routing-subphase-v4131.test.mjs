import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../src/renderer.js',import.meta.url),'utf8');
test('three endpoint phases are separately timed',()=>{for(const phase of ['distributeEndpointAnchors','orthogonalFanOut','reduceFanOutCrossings']) assert.match(source,new RegExp('timedRoutingStage\\("'+phase+'"'));});
test('each endpoint phase consumes the previous result',()=>{assert.match(source,/orthogonalFanOut\(state.edges,anchoredRoutes,state.nodes\)/);assert.match(source,/reduceFanOutCrossings\(state.edges,fannedRoutes,state.nodes\)/);});
