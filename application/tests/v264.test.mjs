import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {proposeSanAlternate,prepareAlternateCommit,commitAlternateRoute,verifyCommittedAlternate,qualifyAlternateLifecycle} from '../src/san-alternate-routes.js';
import {routeViaWaypoints} from '../src/routing.js';
const fixture=JSON.parse(readFileSync(new URL('../fixtures/san-astar-wall-v264.json',import.meta.url)));
function setup(){const nodes=structuredClone(fixture.nodes),edges=structuredClone(fixture.edges),routes=new Map(Object.entries(structuredClone(fixture.routes)));return {nodes,edges,routes,edge:edges[0]};}
function proposal(s){return proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[fixture.expected.step]});}
test('v26.4 obstacle A* reproductible : amélioration réelle',()=>{const s=setup(),p=proposal(s);assert.equal(p.status,'preview');assert.equal(p.before.collisions,1);assert.equal(p.after.collisions,0);assert.ok(p.gain>=fixture.expected.minimumGain);assert.equal(p.step,10)});
test('v26.4 préparation et application reproductibles',()=>{const s=setup(),p=proposal(s),plan=prepareAlternateCommit(p,s.edge,s.nodes,s.edges,s.routes);const result=commitAlternateRoute(s.edge,plan,s.nodes,s.edges,s.routes);assert.equal(result.edgeId,'e');assert.deepEqual(routeViaWaypoints(s.nodes[0],s.nodes[1],s.edge.waypoints,'right','left').points.map(({x,y})=>({x,y})),p.points.map(({x,y})=>({x,y})));assert.equal(verifyCommittedAlternate(s.edge,plan,s.nodes,s.edges,s.routes).after.collisions,0)});
test('v26.4 topologie périmée : commit refusé sans mutation',()=>{const s=setup(),plan=prepareAlternateCommit(proposal(s),s.edge,s.nodes,s.edges,s.routes);s.nodes[2].x+=10;assert.throws(()=>commitAlternateRoute(s.edge,plan,s.nodes,s.edges,s.routes),/obsolète/);assert.equal(s.edge.waypoints,undefined)});
test('v26.4 Fabric B sans route : proposition refusée',()=>{const s=setup();s.edges.push({id:'opposite',fabric:'B'});assert.equal(proposal(s).status,'unavailable')});
test('v26.4 cycle JSON undo redo qualifié',()=>{const s=setup(),plan=prepareAlternateCommit(proposal(s),s.edge,s.nodes,s.edges,s.routes);const result=qualifyAlternateLifecycle({nodes:s.nodes,edges:s.edges},plan,s.routes);assert.ok(result)});
