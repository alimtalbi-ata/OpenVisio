// OpenVisio v33.6 — repli non destructif des propriétés. Auteur : Abdelhalim Talbi.
const button=document.getElementById('inspectorFieldsToggle');
const content=document.getElementById('inspectorContent');
const status=document.getElementById('inspectorFoldStatus');
const key='openvisio.inspector.fold.v336';
let expanded=true;
try{expanded=localStorage.getItem(key)!=='collapsed';}catch{}
function apply(){
 if(!content||!button)return;
 content.hidden=!expanded;
 button.setAttribute('aria-expanded',String(expanded));
 button.textContent=expanded?'▾ Propriétés de la sélection':'▸ Afficher les propriétés';
 if(status)status.textContent=expanded?'':'Panneau replié';
}
button?.addEventListener('click',()=>{expanded=!expanded;try{localStorage.setItem(key,expanded?'expanded':'collapsed');}catch{}apply();});
document.getElementById('inspectSelectionBtn')?.addEventListener('click',()=>{if(!expanded){expanded=true;apply();} });
apply();
