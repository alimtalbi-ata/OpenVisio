import test from "node:test";import assert from "node:assert/strict";import {groupNodes,ungroupNodes,createLayer,setLayer,visibleNode,editableNode} from "../src/organization.js";
test("grouper et dégrouper",()=>{const s={nodes:[{id:"a"},{id:"b"}],groups:[]};const id=groupNodes(s,["a","b"]);assert.ok(id);assert.equal(s.nodes[0].groupId,id);assert.equal(ungroupNodes(s,["a"]),1);assert.equal(s.groups.length,0);});
test("groupe nécessite deux objets",()=>assert.equal(groupNodes({nodes:[{id:"a"}],groups:[]},["a"]),null));
test("calques visibilité et verrouillage",()=>{const s={nodes:[{id:"a"}],layers:[]};const id=createLayer(s,"SAN");assert.equal(setLayer(s,["a"],id),true);const layer=s.layers[0];layer.visible=false;assert.equal(visibleNode(s,s.nodes[0]),false);layer.locked=true;assert.equal(editableNode(s,s.nodes[0]),false);});
test("refuse un calque inexistant",()=>assert.equal(setLayer({nodes:[{id:"a"}],layers:[]},["a"],"missing"),false));
