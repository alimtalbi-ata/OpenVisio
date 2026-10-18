// Auteur : Abdelhalim Talbi
import test from "node:test";
import assert from "node:assert/strict";
import {makeNode,makeEdge,validateGraph,restore,snapshot} from "../src/model.js";
test("makeNode produit un identifiant et des coordonnées",()=>{const n=makeNode({type:"server",name:"Serveur"},10,20);assert.ok(n.id);assert.equal(n.x,10);assert.equal(n.y,20);});
test("validateGraph accepte une connexion valide",()=>{const a=makeNode({type:"server"}),b=makeNode({type:"storage"});assert.equal(validateGraph({nodes:[a,b],edges:[makeEdge(a.id,b.id)]}),true);});
test("validateGraph rejette les extrémités inconnues",()=>{const a=makeNode({type:"server"});assert.equal(validateGraph({nodes:[a],edges:[makeEdge(a.id,"absent")]}),false);});
test("restore résiste à une entrée invalide",()=>{assert.deepEqual(restore("{"),{nodes:[],edges:[],selected:null,groups:[],layers:[],guides:[]});});
test("snapshot/restore préserve le graphe",()=>{const a=makeNode({type:"server"});const state={nodes:[a],edges:[],selected:a.id};assert.deepEqual(restore(snapshot(state)),{...state,groups:[],layers:[],guides:[]});});

test("validateGraph rejette les connexions vers soi-même",()=>{const a=makeNode({type:"server"});assert.equal(validateGraph({nodes:[a],edges:[makeEdge(a.id,a.id)]}),false);});
test("validateGraph accepte un graphe vide",()=>{assert.equal(validateGraph({nodes:[],edges:[]}),true);});
