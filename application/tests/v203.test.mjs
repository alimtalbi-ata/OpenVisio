import test from 'node:test';
import assert from 'node:assert/strict';
import {createHistory} from '../src/history-transaction.js';
const state=()=>({nodes:[],edges:[],groups:[],layers:[],guides:[],selected:null});
test('restauration historique atomique si snapshot endommagé',()=>{const h=createHistory(),s=state();h.checkpoint(s);h.undo[0]='{broken';const before=JSON.stringify(s);assert.throws(()=>h.travel(s,h.undo,h.redo));assert.equal(JSON.stringify(s),before);assert.equal(h.undo.length,1);assert.equal(h.redo.length,0);});
test('refuse navigation historique dans la même pile',()=>{const h=createHistory(),s=state();h.checkpoint(s);assert.throws(()=>h.travel(s,h.undo,h.undo));assert.equal(h.undo.length,1);});
test('refuse une pile étrangère',()=>{const h=createHistory(),s=state();assert.throws(()=>h.travel(s,[],h.redo));});
test('refuse annulation geste avec redo non valide',()=>{const h=createHistory(),s=state();h.checkpoint(s);assert.throws(()=>h.cancelCheckpoint(null));assert.equal(h.undo.length,1);});
test('restaure la sélection et le graphe après annulation',()=>{const h=createHistory(),s=state();h.checkpoint(s);s.nodes.push({id:'n1'});s.selected='n1';assert.equal(h.travel(s,h.undo,h.redo),true);assert.equal(s.selected,null);assert.equal(s.nodes.length,0);assert.equal(h.travel(s,h.redo,h.undo),true);assert.equal(s.selected,'n1');});
