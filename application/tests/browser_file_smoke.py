from pathlib import Path
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/"snapshots";out.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path="/usr/bin/chromium",headless=True,args=["--no-sandbox","--allow-file-access-from-files","--no-proxy-server"])
 page=browser.new_page(viewport={"width":1600,"height":950})
 errors=[]
 page.on("pageerror",lambda e:errors.append(str(e)))
 page.goto((root/"index.html").as_uri(),wait_until="load")
 page.wait_for_timeout(400)
 print("url",page.url,"nodes",page.locator(".shape-card").count(),"errors",errors[:3])
 if page.locator(".shape-card").count()>0:
  page.screenshot(path=str(out/"01-accueil-v96-reel.png"),full_page=True)
  picker=page.locator('select[aria-label="Créer un diagramme depuis un modèle"]')
  if picker.count():
   page.on("dialog",lambda dialog:dialog.accept())
   picker.select_option("san-dual")
   page.wait_for_timeout(250)
   print("diagram",page.locator(".node").count(),page.locator(".edge").count())
   page.screenshot(path=str(out/"02-modele-san-v96-reel.png"),full_page=True)
   if page.locator(".edge-hit").count():
    page.locator(".edge-hit").first.click(force=True)
    page.screenshot(path=str(out/"03-inspecteur-v96-reel.png"),full_page=True)
 browser.close()
