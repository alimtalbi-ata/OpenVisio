import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const read=f=>readFileSync(new URL('../'+f,import.meta.url),'utf8');
test('v33.4 includes layout controls and script',()=>{const html=read('index.html');assert.match(html,/resetPanelLayout/);assert.match(html,/workspace-layout-v334.js/);assert.match(html,/workspace-v334.css/);});
test('v33.4 clamps persisted panel sizes and keyboard resizing',()=>{const js=read('src/workspace-layout-v334.js');assert.match(js,/Number.isFinite/);assert.match(js,/setPointerCapture/);assert.match(js,/ArrowLeft/);assert.match(js,/pointercancel/);});
test('v33.4 respects narrow screens and hidden panels',()=>{const css=read('styles/workspace-v334.css');assert.match(css,/max-width:850px/);assert.match(css,/hidden-panel/);});
