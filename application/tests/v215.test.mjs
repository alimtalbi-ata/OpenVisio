// Auteur : Abdelhalim Talbi — contrat de l’atelier v21.5.
import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../index.html',import.meta.url),'utf8');
const css=readFileSync(new URL('../styles/app.css',import.meta.url),'utf8');
const js=readFileSync(new URL('../src/main.js',import.meta.url),'utf8');
test('bouton canevas seul accessible et non soumis',()=>{assert.match(html,/id="focusCanvasBtn"[^>]*type="button"[^>]*aria-pressed="false"/);});
test('panneaux associés à leur commande ARIA',()=>{assert.match(html,/id="toggleLibraries" aria-controls="libraryPanel" aria-expanded="true"/);assert.match(html,/id="toggleInspector" aria-controls="inspectorPanel" aria-expanded="true"/);});
test('canevas agrandi lorsque les deux panneaux sont masqués',()=>{assert.match(css,/\.workspace:has\(\.library-panel\.hidden-panel\):has\(\.inspector-panel\.hidden-panel\)/);});
test('raccourci clavier et synchronisation des panneaux',()=>{assert.match(js,/e\.shiftKey&&!e\.altKey&&e\.key\.toLowerCase\(\)==="f"/);assert.match(js,/function syncWorkspaceControls/);});
