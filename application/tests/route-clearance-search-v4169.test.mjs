import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {renderRouteClearancePanel} from '../src/route-clearance-view.js';
const data={edges:[{edgeId:'FC-A',errors:1},{edgeId:'SAN-B',reviews:1}]};
function node(){const doc={createElement(tag){return {tag,childNodes:[],attributes:{},setAttribute(k,v){this.attributes[k]=v},append(...a){this.childNodes.push(...a)},addEventListener(){},set textContent(v){this.text=v},get textContent(){return this.text}}}};return {ownerDocument:doc,replaceChildren(...a){this.children=a}};}
test('recherche insensible à la casse sur identifiant',()=>{const c=node();renderRouteClearancePanel(c,data,{search:'san'});assert.equal(c.children[2].childNodes.length,1);assert.match(c.children[2].childNodes[0].childNodes[0].textContent,/SAN-B/)});
test('recherche vide explicite sans altérer diagnostics',()=>{const c=node();renderRouteClearancePanel(c,data,{search:'introuvable'});assert.match(c.children[2].childNodes[0].textContent,/Aucune connexion/);assert.equal(data.edges[0].errors,1)});
test('recherche raccordée au panneau éditeur',()=>{const s=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');assert.match(s,/routeQualitySearch.*addEventListener\('input'/);assert.match(s,/search:\$\('routeQualitySearch'\)/)});
