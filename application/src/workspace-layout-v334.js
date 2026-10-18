// OpenVisio v33.4 — panneau redimensionnable, persistance locale et clavier.
const STORE = 'openvisio.layout.panelWidths.v334';
const LIMITS = { library: [180, 420, 260], inspector: [210, 460, 278] };
const workspace = document.querySelector('.workspace');
const panels = { library: document.getElementById('libraryPanel'), inspector: document.getElementById('inspectorPanel') };
const clamp = (value, [min,max]) => Math.max(min, Math.min(max, Math.round(value)));
let widths = {library:260, inspector:278};
try { const saved=JSON.parse(localStorage.getItem(STORE)||'{}'); for(const side of Object.keys(LIMITS)){if(Number.isFinite(saved[side])) widths[side]=clamp(saved[side],LIMITS[side]);} } catch { /* private browsing or invalid preference */ }
function render(){if(!workspace)return; workspace.style.setProperty('--ov-library-width',widths.library+'px');workspace.style.setProperty('--ov-inspector-width',widths.inspector+'px');}
function save(){try{localStorage.setItem(STORE,JSON.stringify(widths));}catch{/* storage unavailable */}}
function setWidth(side,value){widths[side]=clamp(value,LIMITS[side]);render();}
for(const side of Object.keys(panels)){
 const panel=panels[side];if(!panel)continue;
 const handle=document.createElement('button');handle.type='button';handle.className='ov-resize-handle';handle.setAttribute('aria-label',side==='library'?'Redimensionner la bibliothèque':'Redimensionner l’inspecteur');handle.setAttribute('title','Glisser pour ajuster · Flèches gauche/droite au clavier');handle.setAttribute('aria-orientation','vertical');handle.setAttribute('role','separator');handle.tabIndex=0;panel.append(handle);
 handle.addEventListener('pointerdown',event=>{if(event.button!==0 || window.matchMedia('(max-width:850px)').matches)return;event.preventDefault();const start=event.clientX,initial=widths[side],sign=side==='library'?1:-1;handle.setPointerCapture(event.pointerId);document.body.classList.add('ov-resizing');const move=e=>setWidth(side,initial+sign*(e.clientX-start));const end=()=>{handle.removeEventListener('pointermove',move);document.body.classList.remove('ov-resizing');save();};handle.addEventListener('pointermove',move);handle.addEventListener('pointerup',end,{once:true});handle.addEventListener('pointercancel',end,{once:true});});
 handle.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home'].includes(event.key))return;event.preventDefault();const delta=(event.key==='ArrowLeft'?-1:1)*(side==='library'?1:-1)*(event.shiftKey?30:10);setWidth(side,event.key==='Home'?LIMITS[side][2]:widths[side]+delta);save();});
}
document.getElementById('resetPanelLayout')?.addEventListener('click',()=>{for(const side of Object.keys(LIMITS))widths[side]=LIMITS[side][2];render();save();});
render();
