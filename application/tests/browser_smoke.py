"""Recette réelle Chromium/Playwright. Auteur : Abdelhalim Talbi."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess, time, json
root=Path(__file__).resolve().parents[1]
server=subprocess.Popen(['python3','-m','http.server','18793','--bind','127.0.0.1'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
checks=[]; errors=[]
try:
 time.sleep(1)
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1600,'height':950},device_scale_factor=1)
  page.on('pageerror',lambda e: errors.append(str(e)))
  page.goto('http://127.0.0.1:18793/',wait_until='networkidle',timeout=15000)
  checks.append(['page_loaded',page.locator('#diagramCanvas').count()==1])
  checks.append(['shape_library_loaded',page.locator('.shape-card').count()>0])
  page.screenshot(path=str(root/'snapshots/01-accueil-reel.png'),full_page=True)
  # Charger le vrai modèle par l'interface, sans injection SVG ni modification du DOM.
  picker=page.locator('select[aria-label="Créer un diagramme depuis un modèle"]')
  checks.append(['template_picker',picker.count()==1])
  if picker.count():
   picker.select_option('san-dual')
   page.wait_for_timeout(400)
   checks.append(['san_template_loaded',page.locator('.node').count()==4])
   checks.append(['san_edges_loaded',page.locator('.edge').count()==4])
   page.screenshot(path=str(root/'snapshots/02-san-double-fabric-reel.png'),full_page=True)
   page.locator('.edge-hit').first.click(force=True)
   page.wait_for_timeout(200)
   checks.append(['edge_inspector',page.locator('#prop-style').count()==1])
   page.screenshot(path=str(root/'snapshots/03-inspecteur-connexion-reel.png'),full_page=True)
  checks.append(['no_js_errors',len(errors)==0])
  browser.close()
finally:
 server.terminate();server.wait(timeout=5)
report={'checks':[{'name':n,'passed':ok} for n,ok in checks],'js_errors':errors,'passed':sum(ok for _,ok in checks),'total':len(checks),'capture_type':'real Chromium screenshots of running application'}
(root/'QUALIFICATION-NAVIGATEUR.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
if not all(ok for _,ok in checks):raise SystemExit(1)
