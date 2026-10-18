import {suggestedPorts} from "./ports.js";
// Auteur : Abdelhalim Talbi
let seq = 0;
export const newId = prefix => `${prefix}-${Date.now().toString(36)}-${(++seq).toString(36)}`;
export function makeNode(shape, x=420, y=260) {
 return {id:newId("node"),type:shape.type,vendor:shape.vendor||"Generic",category:shape.category||"compute",x,y,w:shape.w||150,h:shape.h||74,title:shape.name||"Nouvel objet",subtitle:shape.subtitle||"",fill:shape.fill||"#f0f7ff",stroke:shape.stroke||"#7aa9e5",ports:suggestedPorts(shape.type)};
}
export function makeEdge(from,to,label="") { return {id:newId("edge"),from,to,label}; }
export function snapshot(state) { return JSON.stringify({nodes:state.nodes,edges:state.edges,selected:state.selected,groups:state.groups||[],layers:state.layers||[],guides:state.guides||[]}); }
export function restore(raw) { try { const v=JSON.parse(raw); if(Array.isArray(v.nodes)&&Array.isArray(v.edges)) return {...v,groups:v.groups||[],layers:v.layers||[],guides:v.guides||[]}; } catch {} return {nodes:[],edges:[],selected:null,groups:[],layers:[],guides:[]}; }
export function validateGraph({nodes,edges}) {
 const ids = new Set(nodes.map(n=>n.id));
 return edges.every(e=>ids.has(e.from)&&ids.has(e.to)&&e.from!==e.to);
}