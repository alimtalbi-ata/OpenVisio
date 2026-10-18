import test from "node:test";import assert from "node:assert/strict";import {TEMPLATES,createTemplate} from "../src/templates.js";
test("au moins six modèles accessibles",()=>assert.ok(TEMPLATES.length>=6));
test("identifiants uniques",()=>assert.equal(new Set(TEMPLATES.map(t=>t.id)).size,TEMPLATES.length));
for(const t of TEMPLATES)test(`modèle ${t.id} cohérent`,()=>{const g=createTemplate(t.id);assert.ok(g.nodes.length>=3);assert.ok(g.edges.length>=2);const ids=new Set(g.nodes.map(n=>n.id));assert.equal(ids.size,g.nodes.length);for(const e of g.edges){assert.ok(ids.has(e.from));assert.ok(ids.has(e.to));}});
test("modèle inconnu refusé",()=>assert.throws(()=>createTemplate("unknown")));
