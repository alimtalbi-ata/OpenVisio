import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {installToolMenus} from '../src/tool-menus.js';
function target() {
 const listeners=new Map();return {open:false,listeners,addEventListener(type,fn){listeners.set(type,fn)},removeEventListener(type){listeners.delete(type)},emit(type,event={}){listeners.get(type)?.({currentTarget:this,...event})},contains(item){return item===this||item?.owner===this},querySelector(){return {focus(){this.focused=true}}}};
}
function fixture(){const a=target(),b=target();const root=target();root.querySelectorAll=()=>[a,b];root.activeElement=null;return {root,a,b,dispose:installToolMenus(root)};}
test('opening second menu closes first',()=>{const f=fixture();f.a.open=true;f.b.open=true;f.b.emit('toggle');assert.equal(f.a.open,false);assert.equal(f.b.open,true);f.dispose()});
test('outside pointer closes all',()=>{const f=fixture();f.a.open=true;f.root.emit('pointerdown',{target:{}});assert.equal(f.a.open,false);f.dispose()});
test('inside pointer preserves open menu',()=>{const f=fixture();f.a.open=true;f.root.emit('pointerdown',{target:{owner:f.a}});assert.equal(f.a.open,true);f.dispose()});
test('Escape dismisses open menus',()=>{const f=fixture();f.a.open=true;f.root.emit('keydown',{key:'Escape'});assert.equal(f.a.open,false);f.dispose()});
test('cleanup detaches event handlers',()=>{const f=fixture();f.dispose();assert.equal(f.root.listeners.size,0);assert.equal(f.a.listeners.size,0)});
test('closed popups hidden and narrow z-order visible',()=>{const css=fs.readFileSync(new URL('../styles/app.css',import.meta.url),'utf8');assert.match(css,/tool-menu:not\(\[open\]\)/);assert.match(css,/zorder-menu \{ display:flex !important/)});
