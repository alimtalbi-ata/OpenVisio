#!/usr/bin/env python3
"""OpenVisio v26.2: genuine browser E2E against native editor; no simulated screenshot.
Run on Windows for Windows qualification. Author: Abdelhalim Talbi.
"""
import argparse,contextlib,datetime,json,platform,subprocess,sys,time,traceback,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def execute(chromium,port,screenshot):
 try:from playwright.sync_api import sync_playwright
 except ImportError as e:raise RuntimeError('DEPENDENCY_MISSING: pip install playwright') from e
 server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 try:
  for _ in range(50):
   try:urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=.3).close();break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('LOCAL_SERVER_UNAVAILABLE')
  with sync_playwright() as p:
   browser=p.chromium.launch(**({'executable_path':chromium} if chromium else {}),headless=True,args=['--no-sandbox'] if sys.platform!='win32' else [])
   context=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':900});page=context.new_page();errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{port}/',wait_until='load')
   page.locator('[data-shape="server"]').first.click();page.locator('[data-shape="storage"]').first.click()
   nodes=page.locator('#nodesLayer > g');assert nodes.count()>=2,'Native shape insertion failed'
   page.locator('[data-tool="connect"]').first.click();nodes.nth(0).click();nodes.nth(1).click()
   edges=page.locator('#edgesLayer > g');assert edges.count()>=1,'Native connector missing'
   page.locator('[data-tool="select"]').first.click()
   paths=page.locator('#edgesLayer path').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("d"))')
   assert paths and all(x and not any(v in x for v in ('NaN','Infinity','undefined')) for x in paths),'Invalid native SVG path'
   page.locator('#wiringBtn').click();assert page.locator('#wiringDialog').is_visible(),'Wiring report not opened'
   summary=page.locator('#wiringTopologySummary').inner_text()
   assert summary.strip(),'Wiring audit missing'
   page.locator('#closeWiring').click()
   before=edges.count();page.keyboard.press('Control+z');assert edges.count()<before,'Ctrl+Z did not undo connector'
   page.keyboard.press('Control+y');assert edges.count()==before,'Ctrl+Y did not restore connector'
   with page.expect_download() as info:page.locator('#portableExportBtn').click()
   raw=info.value.path().read_bytes();backup=json.loads(raw)
   assert backup['integrity']['algorithm']=='sha256','Backup integrity missing'
   page.on('dialog',lambda d:d.accept());page.locator('#newDiagram').click();assert edges.count()==0,'New diagram did not clear edges'
   page.locator('#portableImportFile').set_input_files({'name':'san-v262.json','mimeType':'application/json','buffer':raw})
   assert edges.count()==before,'Reloaded topology does not preserve connector'
   page.reload(wait_until='load');assert edges.count()==before,'Persisted topology lost on reload'
   assert not errors,'Browser JS errors: '+repr(errors)
   if screenshot:
    target=Path(screenshot);target.parent.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(target),full_page=True)
   context.close();browser.close()
   return {'checks':['native-insert','native-connect','native-svg-geometry','wiring-audit','keyboard-undo','keyboard-redo','signed-json-export','json-import','browser-reload'],'native_edges':before,'capture_kind':'real-chromium','wiring_summary':summary[:300]}
 finally:
  server.terminate()
  with contextlib.suppress(Exception):server.wait(timeout=5)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--chromium');a.add_argument('--port',type=int,default=18772);a.add_argument('--screenshot');a.add_argument('--report');args=a.parse_args()
 result={'version':'26.2','platform':platform.platform(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FAIL','author':'Abdelhalim Talbi'}
 try:result.update(execute(args.chromium,args.port,args.screenshot),status='PASS')
 except Exception as e:result.update(error=str(e),traceback=traceback.format_exc(),reason='ENVIRONMENT_BLOCKED' if any(v in str(e) for v in ('ERR_BLOCKED_BY_ADMINISTRATOR','DEPENDENCY_MISSING','Executable doesn','TargetClosedError')) else 'TEST_FAILURE')
 if args.report:
  p=Path(args.report);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='traceback'},ensure_ascii=False))
 sys.exit(0 if result['status']=='PASS' else 1)
