// Auteur : Abdelhalim Talbi. Import texte limité à des commandes zoning explicites.
import {normalizeWwpn} from './zoning.js';
import {validateZones} from './zoning-document.js';
const clean=s=>String(s||'').trim().replace(/^['"]|['"]$/g,'');
function members(s){return s.split(';').map(clean).filter(Boolean);}
export function parseSanConfig(text,vendor='auto',fabric='A'){
 if(typeof text!=='string'||text.length>2_000_000)throw Error('Configuration absente ou trop volumineuse');
 if(!['A','B'].includes(fabric))throw Error('Fabric invalide');
 const lines=text.split(/\r?\n/),aliases=new Map(),rawZones=[],warnings=[],zonesets=[],activeConfigurations=[];
 const kind=vendor==='auto'?(lines.some(x=>/^\s*(?:fcalias|device-alias|zoneset)\b/i.test(x))?'cisco':'brocade'):vendor;
 if(!['brocade','cisco'].includes(kind))throw Error('Éditeur non reconnu');
 let activeAlias=null,activeZone=null,activeZoneset=null;
 for(let i=0;i<lines.length;i++){
  const line=lines[i].trim();if(!line||line.startsWith('#')||line.startsWith('!'))continue;
  if(kind==='brocade'){
   let cfg=line.match(/^cfgcreate\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(cfg){zonesets.push({name:clean(cfg[1]),vsan:null,zones:members(cfg[2])});continue;}
   cfg=line.match(/^cfgadd\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(cfg){const c=zonesets.find(x=>x.name===clean(cfg[1]));if(c)c.zones.push(...members(cfg[2]));else warnings.push(`Ligne ${i+1}: cfgadd sans cfgcreate`);continue;}
   cfg=line.match(/^cfgenable\s+["']?([^"'\s]+)["']?/i);
   if(cfg){activeConfigurations.push({name:clean(cfg[1]),vsan:null,source:'cfgenable'});continue;}
   let m=line.match(/^alicreate\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(m){aliases.set(clean(m[1]),members(m[2]));continue;}
   m=line.match(/^zonecreate\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(m){rawZones.push({name:clean(m[1]),tokens:members(m[2])});continue;}
   m=line.match(/^aliadd\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(m){aliases.set(clean(m[1]),[...(aliases.get(clean(m[1]))||[]),...members(m[2])]);continue;}
   m=line.match(/^zoneadd\s+["']?([^,"']+)["']?\s*,\s*["']([^"']+)["']/i);
   if(m){const z=rawZones.find(z=>z.name===clean(m[1]));if(z)z.tokens.push(...members(m[2]));else warnings.push(`Ligne ${i+1}: zoneadd sans zonecreate`);continue;}
  }else{
   let m=line.match(/^device-alias\s+name\s+(\S+)\s+pwwn\s+(\S+)/i);
   if(m){aliases.set(m[1],[m[2]]);continue;}
   m=line.match(/^fcalias\s+name\s+(\S+)\s+vsan\s+\d+/i);
   if(m){activeAlias=m[1];continue;}
   m=line.match(/^zone\s+name\s+(\S+)\s+vsan\s+(\d+)/i);
   if(m){activeZone={name:m[1],vsan:Number(m[2]),tokens:[]};rawZones.push(activeZone);activeAlias=null;activeZoneset=null;continue;}
   m=line.match(/^zoneset\s+activate\s+name\s+(\S+)\s+vsan\s+(\d+)/i);
   if(m){activeConfigurations.push({name:m[1],vsan:Number(m[2]),source:'zoneset activate'});activeZoneset=null;continue;}
   m=line.match(/^zoneset\s+name\s+(\S+)\s+vsan\s+(\d+)/i);
   if(m){activeZoneset={name:m[1],vsan:Number(m[2]),zones:[]};zonesets.push(activeZoneset);activeZone=null;activeAlias=null;continue;}
   m=line.match(/^member\s+zone\s+(\S+)/i);
   if(m&&activeZoneset){activeZoneset.zones.push(m[1]);continue;}

   m=line.match(/^member\s+(?:pwwn\s+)?(\S+)/i);
   if(m){if(activeZone)activeZone.tokens.push(m[1]);else if(activeAlias)aliases.set(activeAlias,[...(aliases.get(activeAlias)||[]),m[1]]);else warnings.push(`Ligne ${i+1}: membre hors contexte`);continue;}
   if(/^(?:interface|vsan|config|end|exit)\b/i.test(line)){activeZone=null;activeAlias=null;activeZoneset=null;continue;}
  }
 }
 const zones=[];
 for(const z of rawZones){const resolved=[];
  for(const token of z.tokens){const vals=aliases.get(token)||[token];for(const v of vals){const w=normalizeWwpn(v);if(w)resolved.push(w);else warnings.push(`Zone ${z.name}: membre non résolu ${v}`);}}
  const unique=[...new Set(resolved)];
  // Les exports constructeur ne distinguent pas initiateurs et cibles : aucune attribution inventée.
  zones.push({name:z.name,fabric,vsan:z.vsan??null,initiators:[],targets:[],members:unique});
 }
 const known=new Set(zones.map(z=>`${z.vsan??''}:${z.name}`));
 for(const cfg of zonesets){cfg.zones=[...new Set(cfg.zones)];for(const zone of cfg.zones)if(!known.has(`${cfg.vsan??''}:${zone}`))warnings.push(`Zoneset ${cfg.name}: zone inconnue ${zone}`);}
 for(const a of activeConfigurations)if(!zonesets.some(c=>c.name===a.name&&c.vsan===a.vsan))warnings.push(`Configuration active ${a.name}: zoneset absent du fichier`);
 return {vendor:kind,fabric,aliases:Object.fromEntries(aliases),zones,zonesets,activeConfigurations,warnings,requiresRoleAssignment:true};
}
export function assignSanRoles(parsed,assignments){
 const zones=parsed.zones.map(z=>{const mapping=assignments?.[z.name]||{};return {name:z.name,fabric:z.fabric,initiators:z.members.filter(w=>mapping[w]==='initiator'),targets:z.members.filter(w=>mapping[w]==='target')};});
 return validateZones(zones);
}

// Comparaison déclarative, sans interpréter l'état actif des switches.
export function compareSanZones(imported,declared){
 const key=z=>`${z.fabric}:${z.name}`;
 const existing=new Map(declared.map(z=>[key(z),z]));
 return imported.map(z=>{const other=existing.get(key(z));const members=new Set([...(z.initiators||[]),...(z.targets||[])]);const old=new Set([...(other?.initiators||[]),...(other?.targets||[])]);return {name:z.name,fabric:z.fabric,status:!other?'new':members.size===old.size&&[...members].every(x=>old.has(x))?'identical':'changed',added:[...members].filter(x=>!old.has(x)),removed:[...old].filter(x=>!members.has(x))};});
}

// Rapprochement indicatif: une configuration activée par commande ne prouve pas son état effectif sur le switch.
export function summarizeSanActivation(parsed){
 const active=new Set((parsed.activeConfigurations||[]).map(c=>`${c.vsan??''}:${c.name}`));
 return (parsed.zonesets||[]).map(c=>({name:c.name,vsan:c.vsan,zones:[...c.zones],declaredActive:active.has(`${c.vsan??''}:${c.name}`)}));
}

// v12.8 — analyse de configurations *déclarées*, jamais de l'état réel d'un switch.
export function auditSanZonesets(parsed,declaredZones=[]){
 const normalized=(parsed.zonesets||[]).map(c=>({name:c.name,vsan:c.vsan??null,fabric:parsed.fabric,zones:[...new Set(c.zones||[])]}));
 const active=new Set((parsed.activeConfigurations||[]).map(c=>`${c.vsan??''}:${c.name}`));
 const known=new Set((parsed.zones||[]).map(z=>`${z.vsan??''}:${z.name}`));
 const declared=new Map((declaredZones||[]).map(z=>[`${z.fabric}:${z.vsan??''}:${z.name}`,z]));
 const rows=[];const findings=[];
 for(const c of normalized){
  const enabled=active.has(`${c.vsan??''}:${c.name}`);
  for(const name of c.zones){
   const key=`${c.vsan??''}:${name}`,match=declared.get(`${c.fabric}:${key}`);
   const status=!known.has(key)?'missing-in-import':!match?'missing-in-diagram':'present-in-diagram';
   rows.push({fabric:c.fabric,vsan:c.vsan,zoneset:c.name,zone:name,activationDeclared:enabled,status});
   if(status!=='present-in-diagram')findings.push({code:status,zoneset:c.name,zone:name,vsan:c.vsan});
  }
 }
 for(const a of parsed.activeConfigurations||[])if(!normalized.some(c=>c.name===a.name&&c.vsan===(a.vsan??null)))findings.push({code:'activation-without-zoneset',zoneset:a.name,zone:'',vsan:a.vsan??null});
 return {rows,findings,summary:{zonesets:normalized.length,activationCommands:(parsed.activeConfigurations||[]).length,missing:findings.length}};
}
