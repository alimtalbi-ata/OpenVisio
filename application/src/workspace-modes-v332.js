// v33.2 — contextual navigation without modifying diagram engine or removing controls.
const MODES = Object.freeze({edition:'Édition',san:'Analyse SAN',advanced:'Outils avancés'});
const nav=document.createElement('nav');nav.className='ov-mode-nav';nav.setAttribute('aria-label','Mode de travail');
const label=document.createElement('span');label.className='ov-mode-label';label.textContent='Espace de travail';nav.append(label);
const buttons=new Map();
function applyMode(mode){
 if(!Object.hasOwn(MODES,mode)) mode='edition';
 document.documentElement.dataset.ovMode=mode;
 for(const [name,button] of buttons){button.setAttribute('aria-pressed',String(name===mode));button.classList.toggle('active',name===mode);}
 try{localStorage.setItem('openvisio.workspace.mode',mode);}catch{}
}
for(const [key,name] of Object.entries(MODES)){
 const b=document.createElement('button');b.type='button';b.textContent=name;b.dataset.mode=key;
 b.title=key==='edition'?'Dessiner et modifier le diagramme':key==='san'?'Afficher les analyses de résilience, zoning et SPOF':'Afficher tous les outils spécialisés';
 b.addEventListener('click',()=>applyMode(key));nav.append(b);buttons.set(key,b);
}
const ribbon=document.querySelector('.ribbon');if(ribbon)ribbon.parentNode.insertBefore(nav,ribbon);
let saved='edition';try{saved=localStorage.getItem('openvisio.workspace.mode')||saved;}catch{}
applyMode(saved);
// Show hidden analysis panel when navigated to from a search result, and keep the user in control.
document.addEventListener('click',e=>{
 const target=e.target.closest('a[href^="#"]');if(!target)return;
 const id=target.getAttribute('href').slice(1);if(!id)return;
 const panel=document.getElementById(id);if(panel?.matches('[id^="san" i]'))applyMode('san');
});
