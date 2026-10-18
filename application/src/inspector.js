import {formatLunMasking} from "./lun-masking.js";
import {RELATION_FIELDS} from "./san-relations.js";
import {sanFieldsForNode} from "./san-properties.js";
import {cableDiagnostics,portInventory,fabricDiagnostics,fabricRedundancy} from "./ports.js";
import {suggestedPorts} from "./ports.js";
// Auteur : Abdelhalim Talbi
export function renderInspector(container,state,actions){
 const node=state.nodes.find(n=>n.id===state.selected),edge=state.edges.find(e=>e.id===state.selected);
 container.replaceChildren();
 if(!node&&!edge){container.innerHTML='<div class="inspector-empty"><span>◇</span><strong>Aucun objet sélectionné</strong><p>Sélectionnez une forme ou une connexion pour modifier ses propriétés.</p></div>';return;}
 const add=(label,key,value,kind="text",opts=[])=>{
  const wrap=document.createElement("div");wrap.className="field";const l=document.createElement("label");l.textContent=label;l.htmlFor=`prop-${key}`;wrap.append(l);
  let input;
  if(kind==="select"){input=document.createElement("select");opts.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;input.append(o)});}
  else {input=document.createElement("input");input.type=kind;}
  input.id=`prop-${key}`;input.setAttribute("aria-label",label);input.value=value??"";input.addEventListener("change",()=>actions.update(key,input.value));wrap.append(input);container.append(wrap);
 };
 const heading=document.createElement("div");heading.className="inspector-object";
 const objectType=document.createElement("span");objectType.className="inspector-kind";objectType.textContent=edge?"CONNEXION":"ÉQUIPEMENT";
 const objectName=document.createElement("strong");objectName.textContent=edge?(edge.label||`${edge.from} → ${edge.to}`):(node.title||node.type||"Sans titre");
 heading.append(objectType,objectName);container.append(heading);
 const section=document.createElement("div");section.className="section-label";section.textContent=edge?"Propriétés de connexion":"Propriétés de la forme";container.append(section);
 if(edge){const problems=[...cableDiagnostics(state.nodes,state.edges),...fabricDiagnostics(state.nodes,state.edges)].filter(f=>f.edgeId===edge.id);if(problems.length){const warning=document.createElement("p");warning.className="wiring-diagnostics";warning.textContent="Câblage à vérifier : "+problems.map(p=>p.code+(p.port?" ("+p.port+")":"")).join(", ");container.append(warning);}add("Libellé","label",edge.label);for(const [key,label] of RELATION_FIELDS)add(label,key,edge[key]||"");add("Port source","fromPort",edge.fromPort||"auto","select",["auto","left","right","top","bottom"]);add("Port destination","toPort",edge.toPort||"auto","select",["auto","left","right","top","bottom"]);
 const source=state.nodes.find(n=>n.id===edge.from),target=state.nodes.find(n=>n.id===edge.to);
 add("Interface source","sourceInterface",edge.sourceInterface||"","select",["",...(source?.ports||[])]);
 // Connection-level correlated failure domains are editable just like equipment domains.
 const edgeDomainSection=document.createElement('div');edgeDomainSection.className='section-label';edgeDomainSection.textContent='Résilience SAN — domaines de défaillance de la connexion';container.append(edgeDomainSection);
 for(const [key,label] of [['site','Site'],['chassis','Châssis'],['powerDomain','Domaine électrique / PDU'],['controller','Contrôleur'],['failureDomain','Domaine personnalisé']]) add(label,key,edge[key]||'');
 const edgeDomainHint=document.createElement('p');edgeDomainHint.className='wiring-diagnostics';edgeDomainHint.textContent='Utilisez les mêmes identifiants pour les liens partageant un risque physique. Informations déclaratives.';container.append(edgeDomainHint);
 add("Interface destination","targetInterface",edge.targetInterface||"","select",["",...(target?.ports||[])]);add("Trajet","style",edge.style||"orthogonal","select",["orthogonal","straight","avoid","smart"]);add("Décalage du trajet","offset",edge.offset||0,"number");add("Points de passage (x,y ; x,y)","waypoints",Array.isArray(edge.waypoints)?edge.waypoints.map(p=>`${p.x},${p.y}`).join("; "):"");const btn=document.createElement("button");btn.className="danger";btn.textContent="Supprimer la connexion";btn.addEventListener("click",actions.remove);container.append(btn);return;}
 add("Nom affiché","title",node.title);
 add("Fabric SAN (A/B/SHARED)","fabric",node.fabric||"","select",["","A","B","SHARED"]);
 // Editable documentary failure domains. Blank values remove a dependency.
 const domainSection=document.createElement('div');domainSection.className='section-label';domainSection.textContent='Résilience SAN — domaines de défaillance';container.append(domainSection);
 for(const [key,label] of [['site','Site'],['chassis','Châssis'],['powerDomain','Domaine électrique / PDU'],['controller','Contrôleur'],['failureDomain','Domaine personnalisé']]) add(label,key,node[key]||'');
 const domainHint=document.createElement('p');domainHint.className='wiring-diagnostics';domainHint.textContent='Renseignez le même identifiant pour les équipements partageant une dépendance. Ces valeurs sont déclaratives et ne prouvent pas l’indépendance physique.';container.append(domainHint);
 const inventory=portInventory(state.nodes,state.edges).filter(p=>p.nodeId===node.id);
 if(inventory.length){const panel=document.createElement("div");panel.className="wiring-inventory";const title=document.createElement("strong");title.textContent="Inventaire des ports";panel.append(title);
 for(const entry of inventory){const item=document.createElement("div");item.className="wiring-inventory-item";item.textContent=`${entry.port} · ${entry.family} · ${entry.status==='free'?'libre':entry.status==='used'?'occupé':'conflit'} (${entry.edgeIds.length})`;panel.append(item);}container.append(panel);}
 const redundancy=fabricRedundancy(state.nodes,state.edges).find(r=>r.nodeId===node.id);
 if(redundancy){const info=document.createElement("p");info.className="wiring-diagnostics";info.textContent=`Chemins SAN A/B : ${redundancy.fabrics.join(' + ')||'aucun'} — ${redundancy.redundant?'double fabric détectée':'redondance non démontrée'}`;container.append(info);}

 const sanFields=sanFieldsForNode(node);
 if(sanFields.length){const sanSection=document.createElement("div");sanSection.className="section-label";sanSection.textContent="Chaîne SAN — propriétés documentaires";container.append(sanSection);
 for(const [key,label] of sanFields){const val=Array.isArray(node[key])?node[key].join("; "):(node[key]||"");add(label+(key==="wwpns"?" (format xx:xx:xx:xx:xx:xx:xx:xx)":""),key,val);}
 if(sanFields.some(([key])=>key==='luns')){
 const field=document.createElement('div');field.className='field';const label=document.createElement('label');label.textContent='LUN masking (une association LUN ; WWPN initiateur par ligne)';label.htmlFor='prop-lunMasking';
 const editor=document.createElement('textarea');editor.id='prop-lunMasking';editor.rows=5;editor.style.width='100%';editor.value=formatLunMasking(node.lunMasking);editor.addEventListener('change',()=>actions.update('lunMasking',editor.value));field.append(label,editor);container.append(field);
 }
 const hint=document.createElement("p");hint.className="wiring-diagnostics";hint.textContent="Valeurs séparées par ;. Ces informations sont déclaratives et ne proviennent pas d'une découverte automatique.";container.append(hint);}
 add("Interfaces réseau/SAN (séparées par ;)","ports",Array.isArray(node.ports)?node.ports.join("; "):suggestedPorts(node.type).join("; "));const renameButton=document.createElement('button');renameButton.type='button';renameButton.textContent='Renommer un port et réaffecter ses connexions…';renameButton.title='Prévisualisation et confirmation explicite, opération annulable';renameButton.disabled=!node.ports?.length;renameButton.addEventListener('click',()=>actions.renamePort?.());container.append(renameButton);add("Sous-titre","subtitle",node.subtitle);add("Constructeur","vendor",node.vendor,"select",["Generic","Dell","HPE","IBM","NetApp","Pure Storage","Cisco","Brocade","AWS","Hitachi Vantara","Lenovo","Huawei","Infinidat","Synology","QNAP","TrueNAS"]);
 const row=document.createElement("div");row.className="field-row";container.append(row);
 for(const [label,key] of [["X","x"],["Y","y"]]){const wrap=document.createElement("div");wrap.className="field";const l=document.createElement("label");l.textContent=label;const i=document.createElement("input");i.type="number";i.id=`prop-${key}`;l.htmlFor=i.id;i.setAttribute("aria-label",label);i.value=node[key];i.addEventListener("change",()=>actions.update(key,i.value));wrap.append(l,i);row.append(wrap);}
 add("Couleur de fond","fill",node.fill,"color");add("Couleur du contour","stroke",node.stroke,"color");
 const actionsRow=document.createElement("div");actionsRow.className="inspector-actions";const dup=document.createElement("button");dup.textContent="Dupliquer";dup.addEventListener("click",actions.duplicate);const del=document.createElement("button");del.textContent="Supprimer";del.className="danger";del.addEventListener("click",actions.remove);actionsRow.append(dup,del);container.append(actionsRow);
}