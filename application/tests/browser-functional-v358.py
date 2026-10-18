#!/usr/bin/env python3
"""Recette fonctionnelle navigateur réelle, aucune simulation des opérations de l'éditeur. Auteur: Abdelhalim Talbi."""
import argparse,json,subprocess,sys,time,urllib.request,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--chromium',default='');args=ap.parse_args()
 out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
 result={'schema':'openvisio.functional.v2','status':'FAIL','checks':[],'scope':'Navigateur Chromium sur serveur HTTP local; pas une validation de WebView2 natif'}
 server=None
 try:
  from playwright.sync_api import sync_playwright
  import socket
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(60):
   try:urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=.3).close();break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('Serveur HTTP indisponible')
  with sync_playwright() as p:
   browser=p.chromium.launch(**({'executable_path':args.chromium} if args.chromium else {}),headless=True,args=['--no-sandbox'] if sys.platform!='win32' else [])
   page=browser.new_page(viewport={'width':1440,'height':900},accept_downloads=True)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{port}/',wait_until='load')
   assert page.locator('#diagramCanvas').count()==1,'Canvas absent'
   result['checks'].append({'name':'editor_loaded','status':'PASS'})
   page.locator('[data-shape="server"]').first.click();page.locator('[data-shape="storage"]').first.click()
   assert page.locator('#nodesLayer > g').count()>=2,'Insertion de formes en échec'
   result['checks'].append({'name':'insert_two_shapes','status':'PASS'})
   page.locator('[data-tool="connect"]').first.click();page.locator('#nodesLayer > g').nth(0).click();page.locator('#nodesLayer > g').nth(1).click()
   assert page.locator('#edgesLayer > g').count()>=1,'Connexion absente'
   result['checks'].append({'name':'connect_shapes','status':'PASS'})
   page.locator('#undoBtn').click();assert page.locator('#edgesLayer > g').count()==0,'Undo sans effet'
   page.locator('#redoBtn').click();assert page.locator('#edgesLayer > g').count()>=1,'Redo sans effet'
   result['checks'].append({'name':'undo_redo','status':'PASS'})
   # Export actual diagram JSON and SVG through the same UI controls as the user.
   with page.expect_download(timeout=15000) as download_json:
    page.locator('#saveJsonBtn').click()
   json_file=out/'diagram-export-real.json'
   download_json.value.save_as(str(json_file))
   payload=json.loads(json_file.read_text(encoding='utf-8-sig'))
   assert isinstance(payload,(dict,list)),'JSON export is not an object or list'
   result['checks'].append({'name':'json_export','status':'PASS','bytes':json_file.stat().st_size})
   with page.expect_download(timeout=15000) as download_svg:
    page.locator('#exportBtn').click()
   svg_file=out/'diagram-export-real.svg'
   download_svg.value.save_as(str(svg_file))
   assert '<svg' in svg_file.read_text(encoding='utf-8-sig')[:1000].lower(),'SVG export missing SVG element'
   result['checks'].append({'name':'svg_export','status':'PASS','bytes':svg_file.stat().st_size})
   # Import JSON via native file input, ensure the diagram still contains nodes.
   page.locator('#openJsonInput').set_input_files(str(json_file))
   assert page.locator('#nodesLayer > g').count()>=2,'JSON re-import lost nodes'
   result['checks'].append({'name':'json_reopen','status':'PASS'})
   page.screenshot(path=str(out/'functional-ui-real.png'),full_page=True)
   result['checks'].append({'name':'real_screenshot','status':'PASS'})
   result['page_errors']=errors
   browser.close()
  result['status']='PASS'
 except Exception as exc:
  result['error']=str(exc);result['traceback']=traceback.format_exc()
 finally:
  if server is not None:server.terminate();server.wait(timeout=5)
  (out/'functional-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return 0 if result['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
