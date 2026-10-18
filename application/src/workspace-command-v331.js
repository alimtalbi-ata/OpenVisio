// OpenVisio v33.1 — accessible command launcher, no changes to document engine.
const commands = [
  ['Nouveau diagramme','Fichier', ['newDocument','newFile','btnNew']],
  ['Ouvrir un document','Fichier', ['openDocument','openFile','btnOpen']],
  ['Enregistrer','Fichier', ['saveDocument','saveFile','btnSave']],
  ['Annuler','Édition', ['undoBtn','undo']],
  ['Rétablir','Édition', ['redoBtn','redo']],
  ['Comparer les topologies','Analyse', ['topologyDiffOpen','topologyDiffButton']],
  ['Analyser les SPOF SAN','SAN', ['spofRun']],
  ['Analyser les écarts zoning','SAN', ['sanZoningMatrixRun']],
  ['Recommandations SAN','SAN', 'san-recommendations.html'],
  ['Projection SAN','SAN', 'san-canvas.html'],
  ['Simulation avant / après','SAN', 'san-impact-view.html']
];
const launch=document.createElement('button'); launch.className='ov-command-launch'; launch.type='button'; launch.textContent='⌕  Rechercher une action   Ctrl+K'; launch.setAttribute('aria-haspopup','dialog');
const overlay=document.createElement('div'); overlay.className='ov-command-dialog'; overlay.hidden=true; overlay.innerHTML='<section class="ov-command-box" role="dialog" aria-modal="true" aria-label="Rechercher une action"><div class="ov-command-top"><input type="search" aria-label="Rechercher une action" placeholder="Action, outil SAN, export…"><button type="button" aria-label="Fermer">Esc</button></div><div class="ov-command-results" role="listbox"></div></section>';
document.body.append(launch,overlay);
const input=overlay.querySelector('input'), results=overlay.querySelector('.ov-command-results');
let lastFocus=null;
function close(){overlay.hidden=true;lastFocus?.focus();}
function execute(command){close();if(command[1]==='SAN'){document.querySelector('.ov-mode-nav button[data-mode="san"]')?.click();}const target=command[2];if(typeof target==='string'){location.href=target;return;}const button=target.map(id=>document.getElementById(id)).find(Boolean);if(button&&!button.disabled){button.click();return;}if(command[0]==='Comparer les topologies'){document.getElementById('topologyDiffDialog')?.showModal();return;}if(command[0]==='Ouvrir un document'){document.querySelector('input[type=file]')?.click();return;}if(command[0]==='Enregistrer'){document.dispatchEvent(new KeyboardEvent('keydown',{key:'s',ctrlKey:true,bubbles:true}));return;}results.textContent='Cette action n’est pas disponible dans cet espace.';}
function render(){const query=input.value.trim().toLocaleLowerCase('fr');results.replaceChildren();const matched=commands.filter(c=>(c[0]+' '+c[1]).toLocaleLowerCase('fr').includes(query));if(!matched.length){const p=document.createElement('p');p.className='ov-command-empty';p.textContent='Aucune action trouvée';results.append(p);return;}for(const c of matched){const b=document.createElement('button');b.type='button';b.setAttribute('role','option');const title=document.createElement('span');title.textContent=c[0];const category=document.createElement('small');category.textContent=c[1];b.append(title,category);b.addEventListener('click',()=>execute(c));results.append(b);}}
function open(){lastFocus=document.activeElement;overlay.hidden=false;input.value='';render();input.focus();}
launch.addEventListener('click',open);overlay.querySelector('.ov-command-top button').addEventListener('click',close);overlay.addEventListener('click',e=>{if(e.target===overlay)close();});input.addEventListener('input',render);overlay.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();close();}else if(e.key==='Enter'){e.preventDefault();results.querySelector('button')?.click();}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();overlay.hidden?open():close();}});
