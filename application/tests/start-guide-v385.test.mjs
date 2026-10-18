import test from 'node:test';import assert from 'node:assert/strict';import{readFileSync}from'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');const js=readFileSync(new URL('../src/start-guide-v385.js',import.meta.url),'utf8');
test('three onboarding actions are accessible',()=>{for(const id of ['startGuideBtn','startGuideDialog','startBlank','startOpen','startTemplate','closeStartGuide'])assert.match(html,new RegExp(`id="${id}"`));});
test('existing editor commands are reused',()=>{assert.match(js,/forward\('startBlank','newDiagram'\)/);assert.match(js,/forward\('startOpen','openJsonBtn'\)/);});
test('template picker is discovered dynamically',()=>assert.match(js,/Créer un diagramme depuis un modèle/));
