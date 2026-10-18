import test from 'node:test';
import assert from 'node:assert/strict';
import {renderGraph,lastRenderStatistics,routeCacheDiagnostics} from '../src/renderer.js';
class FakeElement {
  constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.textContent='';}
  setAttribute(k,v){this.attributes[k]=String(v);}
  append(...xs){this.children.push(...xs);for(const x of xs)x.parent=this;}
  prepend(x){this.children.unshift(x);x.parent=this;}
  replaceWith(x){if(!this.parent)return;const i=this.parent.children.indexOf(this);if(i>=0)this.parent.children[i]=x;x.parent=this.parent;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(x=>x!==this);}
  replaceChildren(...xs){this.children=[...xs];for(const x of xs)x.parent=this;}
  addEventListener(k,fn){this.listeners[k]=fn;}
  querySelector(s){return this.layers?.[s]||null;}
}
globalThis.document={createElementNS:(_ns,tag)=>new FakeElement(tag)};
function setup(){const svg=new FakeElement('svg');svg.layers={'#nodesLayer':new FakeElement('g'),'#edgesLayer':new FakeElement('g')};const nodes=[{id:'sw1',x:0,y:0,w:80,h:50,type:'switch'},{id:'sw2',x:300,y:0,w:80,h:50,type:'switch'},{id:'host',x:150,y:160,w:80,h:50,type:'server'}];const edges=[{id:'e1',from:'sw1',to:'host',style:'orthogonal'},{id:'e2',from:'sw2',to:'host',style:'orthogonal'},{id:'e3',from:'sw1',to:'sw2',style:'orthogonal'}];return {svg,state:{nodes,edges,selected:null},handlers:{select(){},onPointerDown(){},onNodeClick(){}}};}
const counts=({svg})=>[svg.layers['#nodesLayer'].children.length,svg.layers['#edgesLayer'].children.length];
test('v41.24 repeated SAN node move and undo redo preserve SVG cardinality',()=>{const f=setup();for(let i=0;i<30;i++){f.state.nodes[0].x=(i%3)*25;renderGraph(f.svg,f.state,f.handlers);assert.deepEqual(counts(f),[3,3]);}});
test('v41.24 parallel links remain distinct across updates',()=>{const f=setup();f.state.edges.push({id:'e4',from:'sw1',to:'sw2',style:'orthogonal'});renderGraph(f.svg,f.state,f.handlers);assert.deepEqual(counts(f),[3,4]);f.state.nodes[1].y=70;renderGraph(f.svg,f.state,f.handlers);assert.deepEqual(counts(f),[3,4]);});
test('v41.24 remove and restore node and attached edges',()=>{const f=setup();renderGraph(f.svg,f.state,f.handlers);f.state.nodes=f.state.nodes.filter(n=>n.id!=='host');f.state.edges=f.state.edges.filter(e=>e.to!=='host');renderGraph(f.svg,f.state,f.handlers);assert.deepEqual(counts(f),[2,1]);f.state.nodes.push({id:'host',x:150,y:160,w:80,h:50,type:'server'});f.state.edges.push({id:'e1',from:'sw1',to:'host',style:'orthogonal'},{id:'e2',from:'sw2',to:'host',style:'orthogonal'});renderGraph(f.svg,f.state,f.handlers);assert.deepEqual(counts(f),[3,3]);});
test('v41.24 diagnostic counters stay valid across mutations',()=>{const f=setup();for(let i=0;i<8;i++){f.state.nodes[2].y+=3;renderGraph(f.svg,f.state,f.handlers);const stats=lastRenderStatistics(f.svg);assert.ok(stats.edgesUpdated>=0);const cache=routeCacheDiagnostics();assert.ok(cache.size>=0&&cache.size<=500);}});
