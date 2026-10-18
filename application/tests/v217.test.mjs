import test from 'node:test';import assert from 'node:assert/strict';
import {commonValue,selectionBounds,selectionKinds} from '../src/multi-inspector-model.js';
import {readFileSync} from 'node:fs';
test('valeur commune et valeur mixte',()=>{assert.deepEqual(commonValue([{fill:'#123456'},{fill:'#123456'}],'fill'),{mixed:false,value:'#123456'});assert.deepEqual(commonValue([{fill:'a'},{fill:'b'}],'fill'),{mixed:true,value:null});});
test('selection vide et valeurs manquantes',()=>{assert.deepEqual(commonValue([],'fill'),{mixed:false,value:null});assert.deepEqual(commonValue([{},{}],'fill'),{mixed:false,value:null});});
test('bornes geometriques sans mutation',()=>{const n=[{x:10,y:20,w:40,h:30},{x:-5,y:30,w:10,h:10}];assert.deepEqual(selectionBounds(n),{x:-5,y:20,width:55,height:30,count:2});assert.equal(n[0].x,10);});
test('geometrie invalide refusee',()=>{assert.equal(selectionBounds([{x:0,y:0,w:NaN,h:1}]),null);assert.equal(selectionBounds([]),null);});
test('types distincts tries',()=>{assert.deepEqual(selectionKinds([{type:'server'},{type:'storage'},{type:'server'}]),['server','storage']);});
test('inspecteur multi applique uniquement aux formes editables',()=>{const js=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');assert.match(js,/const editable=nodes.filter\(n=>editableNode\(state,n\)\)/);assert.match(js,/editable.forEach\(n=>n\[key\]=input.value\)/);assert.match(js,/Calques différents/);});
