// Auteur : Abdelhalim Talbi
import {makeNode,makeEdge} from "./model.js";
import {DEFAULTS} from "./catalog.js";
const node=(type,title,x,y,subtitle="",vendor="Generic")=>({...makeNode({type,...DEFAULTS[type],title,subtitle,vendor},x,y)});
export const TEMPLATES=[
 {id:"san-dual",name:"SAN double fabric",description:"Deux switches FC et deux chemins redondants",create(){
 const host=node("server","Cluster ESXi",110,290,"HBA A / B","VMware"),a=node("switch","Fabric A",380,130,"Brocade / Cisco"),b=node("switch","Fabric B",380,400,"Brocade / Cisco"),array=node("storage","Baie SAN",730,290,"Contrôleurs A / B");
 return {nodes:[host,a,b,array],edges:[makeEdge(host.id,a.id),makeEdge(host.id,b.id),makeEdge(a.id,array.id),makeEdge(b.id,array.id)]};}},
 {id:"replication",name:"Réplication intersites",description:"Source, WAN et baie de destination",create(){
 const source=node("storage","Stockage DC1",110,290,"Site primaire"),wan=node("cloud","WAN intersites",410,290,"Réseau de réplication"),target=node("storage","Stockage DC2",740,290,"Site de secours");
 return {nodes:[source,wan,target],edges:[makeEdge(source.id,wan.id),makeEdge(wan.id,target.id)]};}},
 {id:"backup",name:"Sauvegarde et archivage",description:"Serveur, cible backup et objet",create(){
 const host=node("server","Serveur de production",110,290,"Données applicatives"),backup=node("storage","Appliance backup",420,290,"Sauvegarde immuable"),archive=node("cloud","Archive S3",750,290,"Conservation longue durée");
 return {nodes:[host,backup,archive],edges:[makeEdge(host.id,backup.id),makeEdge(backup.id,archive.id)]};}} ,
 {id:"three-tier",name:"Application 3 tiers",description:"Frontaux, services applicatifs et base de données",create(){
 const front=node("server","Frontaux Web",90,280,"HTTPS / reverse proxy"),app=node("server","Services applicatifs",410,280,"API / traitements"),db=node("storage","Données transactionnelles",760,280,"Stockage et sauvegarde");
 return {nodes:[front,app,db],edges:[makeEdge(front.id,app.id),makeEdge(app.id,db.id)]};}},
 {id:"hybrid-cloud",name:"Infrastructure hybride",description:"Datacenter, interconnexion et cloud public",create(){
 const local=node("server","Datacenter privé",90,280,"Virtualisation / stockage"),link=node("switch","Interconnexion",410,280,"VPN / lien dédié"),cloud=node("cloud","Cloud public",760,280,"Services hébergés");
 return {nodes:[local,link,cloud],edges:[makeEdge(local.id,link.id),makeEdge(link.id,cloud.id)]};}},
 {id:"disaster-recovery",name:"PRA / continuité",description:"Site principal, réplication et reprise",create(){
 const primary=node("server","Production DC1",90,260,"Applications critiques"),replica=node("storage","Réplication",420,260,"Journal / snapshots"),secondary=node("server","Reprise DC2",770,260,"Capacité de secours");
 return {nodes:[primary,replica,secondary],edges:[makeEdge(primary.id,replica.id),makeEdge(replica.id,secondary.id)]};}}

 ,{id:"kubernetes",name:"Plateforme Kubernetes",description:"Ingress, workers, stockage persistant et observabilité",create(){
 const ingress=node("switch","Ingress / Load Balancer",100,250,"Entrée HTTPS"),workerA=node("server","Worker A",400,130,"Pods applicatifs"),workerB=node("server","Worker B",400,370,"Pods applicatifs"),volume=node("storage","Volumes persistants",770,250,"CSI / snapshots");
 return {nodes:[ingress,workerA,workerB,volume],edges:[makeEdge(ingress.id,workerA.id),makeEdge(ingress.id,workerB.id),makeEdge(workerA.id,volume.id),makeEdge(workerB.id,volume.id)]};}}
 ,{id:"zero-trust",name:"Segmentation Zero Trust",description:"Utilisateurs, accès contrôlé et services internes",create(){
 const users=node("cloud","Utilisateurs",80,280,"Identités / MFA"),gateway=node("switch","Passerelle ZTNA",370,280,"Contrôle d'accès"),apps=node("server","Applications",700,150,"Services autorisés"),data=node("storage","Données",700,390,"Accès restreint");
 return {nodes:[users,gateway,apps,data],edges:[makeEdge(users.id,gateway.id),makeEdge(gateway.id,apps.id),makeEdge(gateway.id,data.id)]};}}
 ,{id:"backup-321",name:"Protection 3-2-1",description:"Production, copie locale et copie distante",create(){
 const prod=node("server","Production",80,280,"Données primaires"),local=node("storage","Backup local",370,150,"Copie de restauration"),offsite=node("cloud","Backup hors site",700,300,"Copie isolée / immuable"),verify=node("server","Vérification",370,420,"Tests de restauration");
 return {nodes:[prod,local,offsite,verify],edges:[makeEdge(prod.id,local.id),makeEdge(local.id,offsite.id),makeEdge(local.id,verify.id)]};}}
 ,{id:"observability",name:"Observabilité",description:"Sources, collecte et tableaux de bord",create(){
 const linux=node("server","Serveurs Linux",80,150,"Métriques / logs"),storage=node("storage","Baies de stockage",80,390,"Alertes / capacité"),collect=node("server","Collecteurs",390,270,"Logs / métriques / traces"),dashboard=node("cloud","Dashboards",760,270,"SLO / alerting");
 return {nodes:[linux,storage,collect,dashboard],edges:[makeEdge(linux.id,collect.id),makeEdge(storage.id,collect.id),makeEdge(collect.id,dashboard.id)]};}}

 ,{id:"flowchart",name:"Diagramme de flux",description:"Processus, décision et sorties",create(){
 const start=node("terminator","Début",90,270),step=node("process","Traitement",330,270),choice=node("decision","Validation ?",580,255),yes=node("terminator","Terminé",840,150),no=node("document","Reprise",840,390);
 return {nodes:[start,step,choice,yes,no],edges:[makeEdge(start.id,step.id),makeEdge(step.id,choice.id),makeEdge(choice.id,yes.id,"Oui"),makeEdge(choice.id,no.id,"Non")]};}}
 ,{id:"orgchart",name:"Organigramme",description:"Direction, responsables et équipes",create(){
 const head=node("person","Direction",430,80),a=node("department","Infrastructure",140,310),b=node("department","Production",430,310),c=node("department","Sécurité",720,310);
 return {nodes:[head,a,b,c],edges:[makeEdge(head.id,a.id),makeEdge(head.id,b.id),makeEdge(head.id,c.id)]};}}
 ,{id:"application-map",name:"Cartographie applicative",description:"Utilisateurs, API, applications et base de données",create(){
 const user=node("person","Utilisateurs",60,270),fw=node("firewall","WAF / Firewall",270,270),api=node("api","API Gateway",480,270),app=node("application","Services métier",680,140),db=node("database","Base de données",680,390);
 return {nodes:[user,fw,api,app,db],edges:[makeEdge(user.id,fw.id),makeEdge(fw.id,api.id),makeEdge(api.id,app.id),makeEdge(app.id,db.id)]};}}
];
export function createTemplate(id){const template=TEMPLATES.find(t=>t.id===id);if(!template)throw Error("Unknown template");return template.create();}
