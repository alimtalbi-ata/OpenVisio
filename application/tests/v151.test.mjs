import test from "node:test";
import assert from "node:assert/strict";
import {SHAPES,DEFAULTS} from "../src/catalog.js";
import {TEMPLATES,createTemplate} from "../src/templates.js";
import {validateGraph} from "../src/model.js";
for(const type of ["process","decision","terminator","document","database","person","department","application","api","firewall","router","loadbalancer","container","vm","backup","tape"]){
 test(`Forme vectorielle ${type}`,()=>{assert.ok(SHAPES.some(s=>s.type===type));assert.ok(DEFAULTS[type]);});
}
for(const id of ["flowchart","orgchart","application-map"]){test(`Modèle ${id}`,()=>{const doc=createTemplate(id);assert.ok(doc.nodes.length>=4);assert.ok(doc.edges.length>=3);assert.ok(validateGraph(doc));});}
test("Les modèles sont accessibles dans la bibliothèque",()=>assert.ok(TEMPLATES.length>=13));
