// OpenVisio v38.5 — accueil orienté tâches, sans sauvegarde automatique ni écrasement implicite.
export function wireStartGuide(doc = document) {
  const dialog=doc.getElementById('startGuideDialog');
  if (!dialog || !doc.getElementById('startGuideBtn')) return false;
  const close=()=>dialog.close();
  doc.getElementById('startGuideBtn').addEventListener('click',()=>dialog.showModal());
  doc.getElementById('closeStartGuide').addEventListener('click',close);
  const forward=(from,to)=>doc.getElementById(from).addEventListener('click',()=>{close();doc.getElementById(to)?.click();});
  forward('startBlank','newDiagram');
  forward('startOpen','openJsonBtn');
  doc.getElementById('startTemplate').addEventListener('click',()=>{
    close();
    const picker=doc.querySelector('select[aria-label="Créer un diagramme depuis un modèle"]');
    if(picker){picker.scrollIntoView?.({block:'nearest'});picker.focus();}
    else doc.getElementById('commandSearchBtn')?.click();
  });
  return true;
}
if (typeof document!=='undefined') {
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>wireStartGuide(),{once:true});
  else wireStartGuide();
}
