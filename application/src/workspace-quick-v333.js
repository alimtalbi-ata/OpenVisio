// OpenVisio v33.3: non-destructive contextual navigation for existing features.
const nav=document.querySelector('.ov-mode-nav');
if(nav){
 const quick=document.createElement('div');quick.className='ov-quick-actions';quick.setAttribute('role','group');quick.setAttribute('aria-label','Accès rapide aux fonctions');
 const actions=[['Créer','edition',null],['SPOF SAN','san','sanSpofPanel'],['Zoning','san','sanImportCorrelationPanel'],['Tous les outils','advanced',null]];
 for(const [title,mode,id] of actions){
  const b=document.createElement('button');b.type='button';b.textContent=title;
  b.addEventListener('click',()=>{
   nav.querySelector(`[data-mode="${mode}"]`)?.click();
   if(id){const target=document.getElementById(id);if(target){target.scrollIntoView({behavior:'smooth',block:'start'});target.querySelector('summary')?.click();}}
   if(title==='Créer')document.querySelector('.canvas-toolbar')?.scrollIntoView({behavior:'smooth',block:'nearest'});
  });quick.append(b);
 }
 nav.insertAdjacentElement('afterend',quick);
}
