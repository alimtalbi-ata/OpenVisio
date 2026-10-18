import test from 'node:test';
import assert from 'node:assert/strict';
import {installToolMenus} from '../src/tool-menus.js';
function fixture(){
 const handlers=new Map(), items=Array.from({length:3},(_,i)=>({hidden:false,focus(){root.activeElement=this},id:i}));
 const summary=items[0];const menu={open:true,addEventListener(k,f){this[k]=f},removeEventListener(k){delete this[k]},contains(x){return items.includes(x)},querySelectorAll(){return items},querySelector(){return summary}};
 const root={activeElement:summary,querySelectorAll(){return [menu]},addEventListener(k,f){handlers.set(k,f)},removeEventListener(k){handlers.delete(k)}};
 const dispose=installToolMenus(root);
 const key=(name)=>{let prevented=false;handlers.get('keydown')({key:name,target:root.activeElement,preventDefault(){prevented=true},stopPropagation(){},stopImmediatePropagation(){}});return prevented};
 return {root,menu,items,key,dispose};
}
test('ArrowDown advances focus inside an open menu',()=>{const f=fixture();assert.equal(f.key('ArrowDown'),true);assert.equal(f.root.activeElement,f.items[1]);f.dispose()});
test('ArrowUp wraps from first to last control',()=>{const f=fixture();f.key('ArrowUp');assert.equal(f.root.activeElement,f.items[2]);f.dispose()});
test('Home and End move to first and last',()=>{const f=fixture();f.key('End');assert.equal(f.root.activeElement,f.items[2]);f.key('Home');assert.equal(f.root.activeElement,f.items[0]);f.dispose()});
test('Escape closes and returns focus to summary',()=>{const f=fixture();f.key('ArrowDown');f.key('Escape');assert.equal(f.menu.open,false);assert.equal(f.root.activeElement,f.items[0]);f.dispose()});
test('keyboard handler is removed by cleanup',()=>{const f=fixture();f.dispose();assert.equal(f.root.activeElement,f.items[0]);});
