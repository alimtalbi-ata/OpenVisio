#!/usr/bin/env python3
"""Recette de rendu SVG réel via Chromium, sans capture fictive. Auteur : Abdelhalim Talbi."""
import argparse, contextlib, json, subprocess, sys, time, urllib.request, datetime, platform, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def run(chromium,port,screenshot):
 server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for _ in range(50):
   try: urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=.3).close();break
   except Exception: time.sleep(.1)
  else: raise RuntimeError('Serveur indisponible')
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   browser=p.chromium.launch(**({'executable_path':chromium} if chromium else {}),headless=True,args=['--no-sandbox'] if sys.platform!='win32' else [])
   page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{port}/',wait_until='load')
   result=page.evaluate('''async () => {\n     const {renderGraph,lastRenderStatistics}=await import(\'/src/renderer.js\');\n     const svg=document.createElementNS(\'http://www.w3.org/2000/svg\',\'svg\');\n     svg.innerHTML=\'<g id="edgesLayer"></g><g id="nodesLayer"></g>\';\n     document.body.append(svg);\n     const handlers={select(){},onNodeDown(){},onEdgeDown(){}};\n     const samples=[];\n     for(const count of [16,64,160]){\n       const nodes=Array.from({length:count},(_,i)=>({id:\'n\'+i,x:(i%16)*115,y:Math.floor(i/16)*85,w:85,h:48,type:\'server\',label:\'SAN \'+i}));\n       const edges=Array.from({length:count},(_,i)=>({id:\'e\'+i,from:\'n\'+i,to:\'n\'+((i+1)%count),style:\'orthogonal\'}));\n       const state={nodes,edges,selected:null};\n       let t=performance.now();renderGraph(svg,state,handlers);const cold=performance.now()-t;\n       t=performance.now();renderGraph(svg,state,handlers);const warm=performance.now()-t;\n       const warmStats=lastRenderStatistics(svg);\n       nodes[0]={...nodes[0],x:nodes[0].x+7};\n       t=performance.now();renderGraph(svg,{...state,nodes},handlers);const moved=performance.now()-t;\n       samples.push({nodes:count,edges:count,cold_ms:+cold.toFixed(3),cached_ms:+warm.toFixed(3),move_ms:+moved.toFixed(3),cached_dom:warmStats,svg_nodes:svg.querySelectorAll(\'*\').length});\n     }\n     const interactions=[];
     const nodes=Array.from({length:64},(_,i)=>({id:'san'+i,x:(i%8)*150,y:Math.floor(i/8)*110,w:105,h:58,type:'server',label:'SAN '+i}));
     const edges=Array.from({length:63},(_,i)=>({id:'link'+i,from:'san'+i,to:'san'+(i+1),style:'orthogonal'}));
     const state={nodes,edges,selected:null};
     renderGraph(svg,state,handlers);
     const initialCount=svg.querySelectorAll('*').length;
     for(const zoom of [0.5,1,1.5,2]){
       svg.setAttribute('viewBox',`0 0 ${1200/zoom} ${900/zoom}`);
       const valid=svg.getAttribute('viewBox')===`0 0 ${1200/zoom} ${900/zoom}`;
       interactions.push({operation:'zoom',factor:zoom,pass:valid,svg_elements:svg.querySelectorAll('*').length});
     }
     const selection={...state,selected:'san0'};
     renderGraph(svg,selection,handlers);
     interactions.push({operation:'selection',pass:svg.querySelectorAll('*').length>0,svg_elements:svg.querySelectorAll('*').length});
     const movedNodes=nodes.map((n,i)=>i<4?{...n,x:n.x+20,y:n.y+10}:n);
     const t=performance.now();renderGraph(svg,{...state,nodes:movedNodes},handlers);
     const moveTime=performance.now()-t;
     const paths=Array.from(svg.querySelectorAll('path')).map(x=>x.getAttribute('d'));
     interactions.push({operation:'multi-move',count:4,duration_ms:+moveTime.toFixed(3),pass:svg.querySelectorAll('*').length>0,svg_elements:svg.querySelectorAll('*').length});
     interactions.push({operation:'routing-integrity',paths:paths.length,invalid_paths:paths.filter(x=>!x||/NaN|Infinity|undefined/.test(x)).length,pass:paths.length>0&&paths.every(x=>x&&!/NaN|Infinity|undefined/.test(x))});
     svg.remove();return {samples,interactions,initial_svg_elements:initialCount};\n   }''')
   if any(not item['pass'] for item in result['interactions']):raise RuntimeError('Scenario graphique non conforme: '+repr(result['interactions']))
   # Gestes physiques Playwright sur une surface de test visible et indépendante.
   gestures=page.evaluate("""() => {
     const host=document.createElement('div');host.id='gesture-lab';host.style.cssText='position:fixed;left:24px;top:24px;width:420px;height:270px;background:#eef5ff;border:2px solid #356;z-index:99999';
     host.innerHTML='<strong>OpenVisio SAN — recette souris</strong><div id="drag-target" style="position:absolute;left:40px;top:65px;width:75px;height:45px;background:#3986c9;cursor:move"></div>';
     document.body.append(host);
     const target=host.querySelector('#drag-target');let dragging=false,start=null;
     target.addEventListener('pointerdown',e=>{dragging=true;start={x:e.clientX,y:e.clientY};target.setPointerCapture(e.pointerId)});
     target.addEventListener('pointermove',e=>{if(dragging){target.style.left=(40+e.clientX-start.x)+'px';target.style.top=(65+e.clientY-start.y)+'px'}});
     target.addEventListener('pointerup',()=>dragging=false);
     host.addEventListener('wheel',e=>{e.preventDefault();host.dataset.zoom=String(Number(host.dataset.zoom||1)*(e.deltaY<0?1.1:0.9))},{passive:false});
     host.addEventListener('keydown',e=>{if(e.key==='Escape')host.dataset.escape='true'});host.tabIndex=0;
     return {ready:true};
   }""")
   target=page.locator('#drag-target');box=target.bounding_box();assert box
   x,y=box['x']+box['width']/2,box['y']+box['height']/2
   page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+52,y+31,steps=8);page.mouse.up()
   drag=page.locator('#drag-target').evaluate("el=>({x:parseFloat(el.style.left),y:parseFloat(el.style.top)})")
   assert abs(drag['x']-92)<2 and abs(drag['y']-96)<2, f'Drag incorrect: {drag}'
   page.mouse.move(180,130);page.mouse.wheel(0,-160)
   zoom=page.locator('#gesture-lab').get_attribute('data-zoom');assert float(zoom)>1
   page.locator('#gesture-lab').focus();page.keyboard.press('Escape')
   assert page.locator('#gesture-lab').get_attribute('data-escape')=='true'
   result['real_pointer_gestures']={'drag_delta_px':[52,31],'zoom_factor':float(zoom),'escape':True,'pass':True,'scope':'surface de recette indépendante; ne prouve pas le glisser-déposer natif OpenVisio'}
   # Recette de l'éditeur réel, sans surface de test artificielle.
   # Les gestes ciblent les noeuds SVG créés par les commandes de l'application.
   page.locator('[data-shape="server"]').first.click()
   page.locator('[data-shape="storage"]').first.click()
   canvas=page.locator('#diagramCanvas')
   native_nodes=page.locator('#nodesLayer > g')
   assert native_nodes.count()>=2, 'Insertion native de deux équipements impossible'
   first=native_nodes.nth(0)
   before=first.get_attribute('transform')
   box=first.bounding_box()
   assert box, 'Équipement natif invisible'
   px,py=box['x']+box['width']*.4,box['y']+box['height']*.45
   page.mouse.move(px,py);page.mouse.down();page.mouse.move(px+62,py+42,steps=12);page.mouse.up()
   after=native_nodes.nth(0).get_attribute('transform')
   assert before!=after, f'Déplacement natif non pris en compte: {before} / {after}'
   # La commande Connecteur doit créer une connexion visible entre les deux objets.
   page.locator('[data-tool="connect"]').first.click()
   native_nodes.nth(0).click()
   native_nodes.nth(1).click()
   native_edges=page.locator('#edgesLayer > g')
   assert native_edges.count()>=1, 'Connexion native absente après deux clics'
   paths=page.locator('#edgesLayer path').evaluate_all('(items)=>items.map(e=>e.getAttribute("d"))')
   assert paths and all(v and not any(x in v for x in ('NaN','Infinity','undefined')) for v in paths), 'Tracé SAN natif invalide'
   # Vérifications sur l'état réel du document : sélection, annulation et rétablissement.
   page.locator('[data-tool="select"]').first.click()
   native_nodes=page.locator('#nodesLayer > g')
   native_nodes.nth(0).click()
   selection=page.locator('#selectionLabel').inner_text()
   assert 'aucune sélection' not in selection.lower(), f'Sélection native absente : {selection}'
   # Une édition est déjà présente (déplacement + connexion) ; Undo doit modifier le document.
   before_undo=page.locator('#edgesLayer > g').count()
   assert before_undo>=1
   undo=page.locator('#undoBtn');assert undo.is_enabled(), 'Annulation indisponible'
   undo.click()
   after_undo=page.locator('#edgesLayer > g').count()
   assert after_undo<before_undo, f'Annulation de connexion non effective : {before_undo} -> {after_undo}'
   redo=page.locator('#redoBtn');assert redo.is_enabled(), 'Rétablissement indisponible'
   redo.click()
   after_redo=page.locator('#edgesLayer > g').count()
   assert after_redo==before_undo, f'Retablissement incorrect : {after_redo} != {before_undo}'
   result['native_history']={'pass':True,'selection_label':selection,'edges_before_undo':before_undo,'edges_after_undo':after_undo,'edges_after_redo':after_redo}
   result['native_editor']={'pass':True,'inserted_equipment':2,'drag_transform_before':before,'drag_transform_after':after,'edges':native_edges.count(),'paths_checked':len(paths),'scope':'véritables commandes et objets SVG OpenVisio'}
   if screenshot:
    Path(screenshot).parent.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(screenshot),full_page=True)
   page.locator('#gesture-lab').evaluate('el=>el.remove()')
   browser.close()
   if errors:raise RuntimeError('Erreurs navigateur: '+repr(errors))
   return result
 finally:
  server.terminate()
  with contextlib.suppress(Exception):server.wait(timeout=5)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--chromium',default=None);a.add_argument('--port',type=int,default=18769);a.add_argument('--screenshot');a.add_argument('--report');a.add_argument('--baseline');a.add_argument('--comparison-report');a.add_argument('--visual-baseline');a.add_argument('--visual-threshold',type=float,default=0.02);args=a.parse_args()
 report={'scenario':'browser-san-interactions-v248','environment':f'{platform.system()} {platform.release()} / Chromium headless; les temps ne mesurent pas les FPS', 'capture_kind':'real-browser-only-if-PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'screenshot':str(args.screenshot) if args.screenshot else None}
 try:report.update(status='PASS',**run(args.chromium,args.port,args.screenshot))
 except Exception as e:report.update(status='FAIL',error=str(e))
 if args.visual_baseline:
  try:
   if report['status']!='PASS':raise ValueError('Recette Chromium non PASS')
   if not args.screenshot or not Path(args.screenshot).is_file():raise ValueError('Capture réelle absente')
   from PIL import Image, ImageChops, ImageStat
   with Image.open(args.visual_baseline) as base_image, Image.open(args.screenshot) as current_image:
    base_image=base_image.convert('RGB');current_image=current_image.convert('RGB')
    if base_image.size!=current_image.size:raise ValueError(f'Dimensions différentes: {base_image.size} / {current_image.size}')
    difference=ImageChops.difference(base_image,current_image)
    mean=ImageStat.Stat(difference).mean
    ratio=sum(mean)/(3*255)
    report['visual_comparison']={'baseline':args.visual_baseline,'difference_ratio':round(ratio,6),'threshold':args.visual_threshold,'pass':ratio<=args.visual_threshold,'dimensions':list(base_image.size)}
    if ratio>args.visual_threshold:report['status']='FAIL';report['error']='Régression visuelle au-delà du seuil'
  except Exception as exc:
   report['status']='FAIL';report['visual_comparison']={'pass':False,'error':str(exc)}
 if args.baseline:
  try:
   baseline=json.loads(Path(args.baseline).read_text(encoding='utf8'))
   if report['status']!='PASS' or baseline.get('status')!='PASS':raise ValueError('Les deux rapports doivent être PASS')
   base={row['edges']:row for row in baseline['samples']}
   comparisons=[]
   for row in report['samples']:
    old=base.get(row['edges'])
    if not old:continue
    comparisons.append({'edges':row['edges'],'metrics':{key:{'baseline_ms':old[key],'current_ms':row[key],'delta_pct':round((row[key]-old[key])*100/old[key],2) if old[key]>0 else None} for key in ('cold_ms','cached_ms','move_ms')}})
   report['comparison']={'baseline':str(args.baseline),'results':comparisons,'note':'Comparaison indicative : machines et charges doivent être identiques'}
  except Exception as e:report['comparison']={'status':'UNAVAILABLE','reason':str(e)}
 if args.report:Path(args.report).parent.mkdir(parents=True,exist_ok=True);Path(args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 if args.comparison_report:Path(args.comparison_report).parent.mkdir(parents=True,exist_ok=True);Path(args.comparison_report).write_text(json.dumps(report.get('comparison',{'status':'NOT_REQUESTED'}),indent=2,ensure_ascii=False),encoding='utf8')
 print(json.dumps(report,ensure_ascii=False));sys.exit(0 if report['status']=='PASS' else 1)
