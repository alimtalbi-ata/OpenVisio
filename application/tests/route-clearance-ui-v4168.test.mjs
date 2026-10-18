import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildRouteClearanceView,renderRouteClearancePanel} from '../src/route-clearance-view.js';
const edges={edges:[{edgeId:'A',errors:1,reviews:0,issues:[]},{edgeId:'B',errors:0,reviews:1,issues:[]},{edgeId:'C',errors:0,reviews:0,issues:[]}]};
function fakeDoc(){return {createElement(tag){return {tag,childNodes:[],attributes:{},setAttribute(k,v){this.attributes[k]=v},append(...x){this.childNodes.push(...x)},addEventListener(k,fn){this[k]=fn},set textContent(x){this.text=x},get textContent(){return this.text}}}}}
test('panneau présente un bilan lisible et les filtres',()=>{const el={ownerDocument:fakeDoc(),replaceChildren(...x){this.children=x}};renderRouteClearancePanel(el,edges,{filter:'error'});assert.match(el.children[1].textContent,/3 connexion/);assert.equal(el.children[2].childNodes.length,1)});
test('connexion sélectionnée signalée sans modifier le diagnostic',()=>{const el={ownerDocument:fakeDoc(),replaceChildren(...x){this.children=x}};let selected='';renderRouteClearancePanel(el,edges,{selectedEdgeId:'B',onSelect:id=>selected=id});const selectedLi=el.children[2].childNodes[1];assert.equal(selectedLi.attributes['data-selected'],'true');assert.equal(selectedLi.childNodes[0].attributes['aria-current'],'true');selectedLi.childNodes[0].click();assert.equal(selected,'B');assert.equal(edges.edges[1].reviews,1)});
test('sélection courante transmise depuis éditeur',()=>{const src=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');assert.match(src,/selectedEdgeId:state.selected/)});
