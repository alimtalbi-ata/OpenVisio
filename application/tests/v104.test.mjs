import test from "node:test";import assert from "node:assert/strict";import {TEMPLATES,createTemplate} from "../src/templates.js";
test("dix modèles distincts",()=>{assert.ok(TEMPLATES.length>=10);assert.equal(new Set(TEMPLATES.map(x=>x.id)).size,TEMPLATES.length)});
for(const id of ["kubernetes","zero-trust","backup-321","observability"])test(`topologie ${id}`,()=>{const graph=createTemplate(id);const ids=new Set(graph.nodes.map(x=>x.id));assert.equal(ids.size,4);assert.ok(graph.edges.length>=3);for(const edge of graph.edges){assert.ok(ids.has(edge.from));assert.ok(ids.has(edge.to));}});
