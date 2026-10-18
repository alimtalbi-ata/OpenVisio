// OpenVisio v31.1 — imports hors ligne, preuves déclaratives. Auteur : Abdelhalim Talbi.
// Extraits textuels uniquement : ne pas considérer l'absence d'une ligne comme preuve d'absence de zoning.
export const normalizeWwpn = value => {
 const compact=String(value??'').trim().replace(/[:-]/g,'').toLowerCase();
 return /^[0-9a-f]{16}$/.test(compact)?compact.match(/../g).join(':'):null;
};
const tokens=line=>[...String(line).matchAll(/(?:[0-9a-f]{2}:){7}[0-9a-f]{2}|(?:[0-9a-f]{4}:){3}[0-9a-f]{4}/gi)].map(m=>normalizeWwpn(m[0])).filter(Boolean);
const uniq=arr=>[...new Set(arr)];
const safeName=x=>String(x??'').trim().slice(0,128);
export function importSanConfiguration(text,{vendor='auto',source=''}={}){
 if(typeof text!=='string'||text.length>5_000_000)throw new Error('Export texte invalide ou trop volumineux (maximum 5 Mo)');
 const lines=text.replace(/\r\n?/g,'\n').split('\n');
 const zones=[],aliases=[],hostPaths=[],warnings=[];
 let current=null,section='';
 let effective=false; // Only explicit effective-configuration blocks are treated as active.
 for(let n=0;n<lines.length;n++){
  const line=lines[n].trim();if(!line||line.startsWith('#'))continue;
  if(/^effective configuration\s*:/i.test(line)){effective=true;current=null;section='';continue;}
  if(/^(?:defined configuration|cfgshow|running-config)\s*:/i.test(line)){effective=false;current=null;section='';continue;}
  // Brocade cfgshow / zoneshow: zone: name; member list; alias: name; member list.
  let m=line.match(/^(zone|alias)\s*:\s*(\S+)(.*)$/i);
  if(m){section=m[1].toLowerCase();current={name:safeName(m[2]),members:uniq([...tokens(m[3]),...m[3].split(/[;,\s]+/).filter(x=>x&&!normalizeWwpn(x)&&!/^(?:[0-9a-f]{2}:){7}[0-9a-f]{2}$/i.test(x))]),line:n+1,...(section==='zone'?{configurationState:effective?'active':'unknown'}:{})};(section==='zone'?zones:aliases).push(current);continue;}
  // Cisco MDS running-config: zone name X vsan N, member pwwn X; fcalias name X vsan N.
  m=line.match(/^(zone|fcalias)\s+name\s+(\S+)(?:\s+vsan\s+(\d+))?/i);
  if(m){section=m[1]==='zone'?'zone':'alias';current={name:safeName(m[2]),vsan:m[3]??null,members:[],line:n+1,...(section==='zone'?{configurationState:'configured'}:{})};(section==='zone'?zones:aliases).push(current);continue;}
  if(/^(zoneset|device-alias|interface|switchname|cfg:|effective configuration)/i.test(line)){current=null;section='';}
  if(current){const member=line.match(/^member\s+(?:pwwn|fcalias)\s+(\S+)/i);current.members=uniq([...current.members,...tokens(line),...(member?[member[1]]:[])]);continue;}
  // ESXi esxcli storage core path list: capture only explicit path states; no WWPN inferred.
  m=line.match(/^(?:Runtime Name|Device|State|Adapter):\s*(.+)$/i);
  if(m){const key=m[0].split(':')[0].toLowerCase();if(key==='runtime name'){hostPaths.push({runtimeName:safeName(m[1]),sourceLine:n+1,active:false});}
   else if(hostPaths.length){const h=hostPaths.at(-1);if(key==='state')h.active=/^(active|on)$/i.test(m[1].trim());if(key==='device')h.device=safeName(m[1]);if(key==='adapter')h.adapter=safeName(m[1]);} }
 }
 for(const z of zones){if(!z.members.length)warnings.push({code:'ZONE_MEMBERS_UNRESOLVED',line:z.line,name:z.name});}
 return {schema:'openvisio-san-import-v1',vendor,sources:[safeName(source)],zones,aliases,hostPaths,warnings,limitations:['Import partiel de texte Brocade/Cisco/ESXi; aucune configuration active attestée','État actif uniquement si bloc effective configuration explicite; masking et multipathing non inférés']};
}
export function compareImportedZonesToDiagram(imported,expectedPairs=[]){
 const zones=imported?.zones??[];
 return expectedPairs.map(pair=>{const a=normalizeWwpn(pair.initiatorWwpn),b=normalizeWwpn(pair.targetWwpn);const matches=a&&b?zones.filter(z=>z.members.includes(a)&&z.members.includes(b)).map(z=>z.name):[];return {initiatorWwpn:a,targetWwpn:b,status:!a||!b?'UNKNOWN_WWPN':!zones.length?'NO_ZONE_EVIDENCE':matches.length?'DOCUMENTED_PAIR':'PAIR_NOT_IN_IMPORT',zones:matches};});
}
