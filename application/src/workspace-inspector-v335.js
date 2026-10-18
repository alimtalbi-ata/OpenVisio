// OpenVisio v33.5 — filtres non destructifs des champs de l’inspecteur. Auteur : Abdelhalim Talbi.
const host=document.getElementById('inspectorContent');
const mode=document.getElementById('inspectorFilter');
const search=document.getElementById('inspectorFieldSearch');
const count=document.getElementById('inspectorFieldCount');
const inspectorCategory = () => document.querySelector('[data-inspector-category][aria-pressed="true"]')?.dataset.inspectorCategory || 'all';
const fieldCategory = key => /site|chassis|powerdomain|controller|failuredomain/i.test(key)?'resilience':/fabric|wwpn|lun|vsan|zoning|hba|storage/i.test(key)?'san':/fromport|toport|source|target|port|edge|link/i.test(key)?'connections':/fill|stroke|color|font|style|opacity|width|height/i.test(key)?'appearance':'general';
const ESSENTIAL=new Set(['title','label','fabric','vendor','subtitle','fill','stroke','x','y','style','fromPort','toPort']);
const STORAGE_KEY='openvisio.inspector.mode.v335';
try {if(localStorage.getItem(STORAGE_KEY)==='all')mode.value='all';}catch{}
function filter(){
 if(!host)return;
 const query=(search?.value||'').trim().toLocaleLowerCase();let visible=0,total=0;
 for(const field of host.querySelectorAll('.field')){
  const label=field.querySelector('label')?.textContent||'';
  const input=field.querySelector('input,select,textarea');
  const key=input?.id?.replace(/^prop-/,'')||'';
  const sanKeys=/fabric|site|chassis|powerdomain|controller|failuredomain|wwpn|lun|vsan|zoning/i;
  const matches=!query||(query==='@san'?sanKeys.test(key+' '+label):label.toLocaleLowerCase().includes(query)||key.toLocaleLowerCase().includes(query));
  const category=inspectorCategory();
  const categoryMatch=Boolean(query)||category==='all'||fieldCategory(key)===category;
  const essential=Boolean(query)||mode.value==='all'||ESSENTIAL.has(key);
  field.hidden=!(matches&&essential&&categoryMatch);total++;if(!field.hidden)visible++;
 }
 if(count)count.textContent=total?`${visible} / ${total} champs`:'Sélectionnez un objet';
}
mode?.addEventListener('change',()=>{try{localStorage.setItem(STORAGE_KEY,mode.value);}catch{}filter();});
search?.addEventListener('input',filter);
document.addEventListener('openvisio:canvas-painted',filter);
document.addEventListener('openvisio:inspector-refilter',filter);
filter();
