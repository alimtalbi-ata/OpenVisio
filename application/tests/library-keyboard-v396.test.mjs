import test from 'node:test';
import assert from 'node:assert/strict';
import {libraryShortcut,installLibraryKeyboard} from '../src/library-keyboard-v396.js';
const ev=(extra={})=>({key:'/',ctrlKey:false,metaKey:false,altKey:false,shiftKey:false,defaultPrevented:false,target:{closest:()=>null},...extra});
test('slash focuses library',()=>assert.equal(libraryShortcut(ev()),'focus'));
test('ignore typing and modal contexts',()=>{assert.equal(libraryShortcut(ev({target:{closest:()=>({})}})),null);assert.equal(libraryShortcut(ev({ctrlKey:true})),null);assert.equal(libraryShortcut(ev({key:'x'})),null)});
test('delegate to existing shape search field',()=>{let handler,focus=0,prevent=0;const doc={addEventListener:(_,f)=>handler=f,getElementById:()=>({focus:()=>focus++,select:()=>{}})};installLibraryKeyboard(doc);handler(ev({preventDefault:()=>prevent++}));assert.equal(focus,1);assert.equal(prevent,1)});
