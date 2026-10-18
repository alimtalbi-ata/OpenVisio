// OpenVisio v28.3 — contextualisation SAN, sans mutation. Auteur : Abdelhalim Talbi.
export function buildSanContext(overlay, corrections, diagram, objectId) {
 const id=String(objectId ?? '');
 const objects=Array.isArray(diagram?.objects)?diagram.objects:[];
 const connections=Array.isArray(diagram?.connections)?diagram.connections:[];
 const obj=objects.find(x=>String(x.id)===id);
 if(!obj)return {found:false,objectId:id,corrections:[],paths:[],warnings:['Objet absent du diagramme']};
 const marks=(overlay?.marks??[]).filter(m=>m.objectId===id);
 const related=[...new Set(marks.map(m=>m.correctionId))];
 const fixes=related.map(cid=>corrections.find(c=>String(c.id)===cid)).filter(Boolean).map(c=>({id:String(c.id),title:String(c.title??c.name??c.id),risk:String(c.risk??'non renseigné'),fabric:String(c.fabric??'UNKNOWN'),description:String(c.description??''),status:String(c.status??'proposed')}));
 const paths=connections.filter(c=>String(c.sourceId??c.from??c.source)===id||String(c.targetId??c.to??c.target)===id).map(c=>({id:String(c.id??''),fabric:String(c.fabric??'UNKNOWN'),peerId:String(String(c.sourceId??c.from??c.source)===id?(c.targetId??c.to??c.target):(c.sourceId??c.from??c.source))}));
 return {found:true,objectId:id,name:String(obj.name??obj.label??id),corrections:fixes,paths,warnings:(overlay?.warnings??[]).filter(w=>w.includes(id))};
}
export function correctionObjectIds(overlay, correctionId){return [...new Set((overlay?.marks??[]).filter(m=>m.correctionId===String(correctionId)).map(m=>m.objectId))]}
