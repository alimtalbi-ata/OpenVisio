// Benchmark des créations d'éléments SVG dans un DOM simulé, pas du rendu graphique navigateur.
import {renderGraph} from "../src/renderer.js";
import {generateTopology} from "../src/benchmark.js";
import {writeFileSync} from "node:fs";
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.attributes={};this.listeners={};this.textContent="";}
 setAttribute(k,v){this.attributes[k]=v;}
 append(...elements){this.children.push(...elements);elements.forEach(e=>e.parent=this);}
 prepend(el){this.children.unshift(el);}
 replaceWith(el){if(!this.parent)return;const i=this.parent.children.indexOf(this);if(i>=0){this.parent.children[i]=el;el.parent=this.parent;}}
 remove(){if(!this.parent)return;this.parent.children=this.parent.children.filter(x=>x!==this);}

 replaceChildren(...els){this.children=[...els];els.forEach(e=>e.parent=this);}
 addEventListener(k,fn){this.listeners[k]=fn;}
 querySelector(sel){return this.layers?.[sel]||null;}
}
globalThis.document={createElementNS:(_ns,tag)=>new Element(tag)};
const svg=new Element("svg");svg.layers={"#nodesLayer":new Element("g"),"#edgesLayer":new Element("g")};
const handlers={select(){},onPointerDown(){},onNodeClick(){}};
const results=[];
for(const count of [100,500,1000]){
 const graph=generateTopology(count);
 const nodes=graph.nodes.map(n=>({...n,type:"server",fill:"#edf5ff",stroke:"#2563eb",subtitle:"synthetic"}));
 const state={nodes,edges:graph.edges,selected:null};
 const before=performance.now();renderGraph(svg,state,handlers);const coldMs=performance.now()-before;
 const beforeWarm=performance.now();renderGraph(svg,state,handlers);const warmMs=performance.now()-beforeWarm;
 const countElements=(element)=>1+element.children.reduce((sum,child)=>sum+countElements(child),0);
 results.push({nodes:count,edges:graph.edges.length,coldMs,warmMs,svgElements:countElements(svg.layers["#nodesLayer"])+countElements(svg.layers["#edgesLayer"])});
}
const report={scope:"SVG DOM creation in simulated JS DOM; excludes browser layout, paint, interaction and memory",environment:{node:process.version,platform:process.platform},results};
writeFileSync(new URL("../BENCHMARK-SVG-RESULTS.json",import.meta.url),JSON.stringify(report,null,2));
console.table(results);
