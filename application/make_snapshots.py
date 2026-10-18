from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
html=(root/"index.html").read_text()
css=(root/"styles/app.css").read_text()
html=html.replace('<link rel="stylesheet" href="styles/app.css">',"<style>"+css+"</style>")
html=html.replace('<script type="module" src="src/main.js"></script>',"")
shots=root/"snapshots";shots.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path="/usr/bin/chromium",headless=True,args=["--no-sandbox"])
 page=browser.new_page(viewport={"width":1600,"height":950},device_scale_factor=1)
 page.set_content(html,wait_until="load")
 page.screenshot(path=str(shots/"01-interface-accueil.png"),full_page=True)
 page.evaluate("""() => {
 const g=document.getElementById('nodesLayer');
 g.innerHTML='<g class="node" transform="translate(220 220)"><rect width="180" height="100" rx="12" fill="#e7f1ff" stroke="#3b82f6" stroke-width="2"/><text x="90" y="43" text-anchor="middle" font-size="21">▤</text><text x="90" y="68" text-anchor="middle" font-size="16">Cluster ESXi</text></g><g class="node" transform="translate(780 220)"><rect width="180" height="100" rx="12" fill="#e7f1ff" stroke="#3b82f6" stroke-width="2"/><text x="90" y="43" text-anchor="middle" font-size="21">▱</text><text x="90" y="68" text-anchor="middle" font-size="16">Stockage SAN</text></g>';
 document.getElementById('edgesLayer').innerHTML='<path d="M 400 270 L 780 270" fill="none" stroke="#3b82f6" stroke-width="3"/>';
 document.getElementById('emptyState').style.display='none';
 document.getElementById('objectCount').textContent='2 objets · 1 connexion';
 document.getElementById('selectionLabel').textContent=' · 1 connexion sélectionnée';
 document.getElementById('inspectorContent').innerHTML='<div class="section-label">Propriétés de connexion</div><div class="field"><label>Libellé</label><input value="Fibre Channel"></div><div class="field"><label>Trajet</label><select><option>orthogonal</option></select></div><div class="field"><label>Points de passage</label><input value="580,270"></div>';
 }""")
 page.screenshot(path=str(shots/"02-canevas-connecteur-apercu.png"),full_page=True)
 page.evaluate("""() => {
 document.getElementById('edgesLayer').innerHTML='<path d="M 400 270 L 590 270 L 590 420 L 780 420" fill="none" stroke="#3b82f6" stroke-width="3"/><circle cx="590" cy="270" r="9" fill="#fff" stroke="#2563eb" stroke-width="3"/><circle cx="590" cy="420" r="9" fill="#fff" stroke="#2563eb" stroke-width="3"/>';
 }""")
 page.screenshot(path=str(shots/"03-points-de-passage-apercu.png"),full_page=True)
 browser.close()
print("Captures statiques créées :", len(list(shots.glob("*.png"))))
