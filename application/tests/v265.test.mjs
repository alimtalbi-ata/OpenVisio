import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {performance} from 'node:perf_hooks';
import {proposeSanAlternate,prepareAlternateCommit,commitAlternateRoute,verifyCommittedAlternate} from '../src/san-alternate-routes.js';
const fixture=JSON.parse(readFileSync(new URL('../fixtures/san-astar-multiwall-v265.json',import.meta.url)));
function setup(){const nodes=structuredClone(fixture.nodes),edges=structuredClone(fixture.edges),routes=new Map(Object.entries(structuredClone(fixture.routes)));return {nodes,edges,routes,edge:edges[0]};}
test('v26.5 : multi-obstacles, alternative sans collision',()=>{const s=setup(),p=proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[10]});assert.equal(p.status,'preview');assert.ok(p.before.collisions>=3);assert.equal(p.after.collisions,0);});
test('v26.5 : multi-obstacles, application et contrôle',()=>{const s=setup(),p=proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[10]}),plan=prepareAlternateCommit(p,s.edge,s.nodes,s.edges,s.routes);commitAlternateRoute(s.edge,plan,s.nodes,s.edges,s.routes);assert.equal(verifyCommittedAlternate(s.edge,plan,s.nodes,s.edges,s.routes).after.collisions,0);});
test('v26.5 : Fabric B géométrie absente refuse toute proposition',()=>{const s=setup();s.edges.push({id:'fabric-b',from:'a',to:'b',fabric:'B'});assert.equal(proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[10]}).status,'unavailable');});
test('v26.5 : obstacle modifié invalide le commit',()=>{const s=setup(),p=proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[10]}),plan=prepareAlternateCommit(p,s.edge,s.nodes,s.edges,s.routes);s.nodes[3].x+=5;assert.throws(()=>commitAlternateRoute(s.edge,plan,s.nodes,s.edges,s.routes),/obsolète/);assert.equal(s.edge.waypoints,undefined);});
test('v26.5 : recherche bornée avec obstacles nombreux',()=>{const s=setup();for(let i=0;i<50;i++)s.nodes.push({id:'remote'+i,x:1000+i*30,y:800,w:10,h:10});const start=performance.now();const p=proposeSanAlternate(s.edge,s.nodes,s.routes,s.edges,{steps:[10]});assert.equal(p.status,'preview');assert.ok(performance.now()-start<10000);});
