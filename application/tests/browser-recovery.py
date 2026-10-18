#!/usr/bin/env python3
"""Recette Chromium réelle : nécessite playwright et un navigateur Chromium accessible.
Usage: python tests/browser-recovery.py --chromium /chemin/vers/chromium
Ne modifie aucun profil utilisateur (contexte éphémère). Auteur : Abdelhalim Talbi.
"""
import argparse, contextlib, json, subprocess, sys, time, urllib.request, traceback, datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
def run(chromium=None, port=18765, screenshot=None):
    server=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=.3).close();break
            except Exception: time.sleep(.1)
        else: raise RuntimeError('Serveur local indisponible')
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox'] if chromium else [])
            context=browser.new_context(accept_downloads=True,viewport={'width':1440,'height':900})
            page=context.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            url=f'http://127.0.0.1:{port}/'
            page.goto(url,wait_until='load')
            assert not errors, 'Erreurs JavaScript au démarrage : '+repr(errors)
            page.locator('#addFirstShape').click()
            assert '1 objet' in page.locator('#objectCount').inner_text(), 'Ajout de forme impossible'
            page.locator('.quick-actions-more > summary').click()
            with page.expect_download() as download_info: page.locator('#portableExportBtn').click()
            download=download_info.value
            raw=download.path().read_text(encoding='utf-8')
            backup=json.loads(raw)
            assert backup['version']==2, 'Sauvegarde SHA-256 v2 attendue'
            assert backup['integrity']['algorithm']=='sha256'
            assert len(backup['integrity']['value'])==64
            # Une sauvegarde modifiée doit être rejetée sans changer le document.
            tampered=json.loads(raw);tampered['document']+=' '
            page.locator('#portableImportFile').set_input_files({'name':'tampered.json','mimeType':'application/json','buffer':json.dumps(tampered).encode('utf-8')})
            assert '1 objet' in page.locator('#objectCount').inner_text(), 'Import corrompu a modifié le diagramme'
            page.locator('#recoveryStatusBtn').click()
            assert page.locator('#recoveryStatusDialog').is_visible(), 'Diagnostic inaccessible'
            assert page.locator('#recoveryPrimaryStatus').inner_text().strip(), 'Diagnostic primaire absent'
            page.locator('#recoveryCloseBtn').click()
            page.locator('.quick-actions-more > summary').click()
            page.on('dialog',lambda d:d.accept())
            page.locator('#newDiagram').click()
            assert '0 objet' in page.locator('#objectCount').inner_text()
            page.locator('#portableImportFile').set_input_files({'name':'backup.json','mimeType':'application/json','buffer':raw.encode('utf-8')})
            assert '1 objet' in page.locator('#objectCount').inner_text(), 'Restauration non appliquée'
            page.reload(wait_until='load')
            assert '1 objet' in page.locator('#objectCount').inner_text(), 'Persistance après redémarrage absente'
            # Créer une nouvelle révision depuis le ruban (l'état vide est masqué).
            page.locator('[data-shape=server]').click()
            assert '2 objets' in page.locator('#objectCount').inner_text()
            # Provoquer une corruption et accepter explicitement la récupération.
            page.evaluate("localStorage.setItem('openvisio-document-v206','{corrupt')")
            page.reload(wait_until='load')
            assert '1 objet' in page.locator('#objectCount').inner_text(), 'Récupération secours impossible'
            page.locator('.quick-actions-more > summary').click()
            page.locator('#recoveryStatusBtn').click()
            assert page.locator('#recoveryStatusSummary').inner_text().strip(), 'Diagnostic post-récupération absent'
            page.locator('#recoveryCloseBtn').click()
            if screenshot:
                Path(screenshot).parent.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(screenshot),full_page=True)
            assert not errors, 'Erreurs JavaScript : '+repr(errors)
            context.close();browser.close()
    finally:
        server.terminate()
        with contextlib.suppress(Exception):server.wait(timeout=5)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--chromium');a.add_argument('--port',type=int,default=18765);a.add_argument('--screenshot');a.add_argument('--report');args=a.parse_args()
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        run(args.chromium,args.port,args.screenshot)
        result={'status':'PASS','started_utc':started,'scenario':'browser-recovery','screenshot':args.screenshot}
    except Exception as exc:
        msg=str(exc)
        reason='ENVIRONMENT_BLOCKED' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in msg else 'TEST_FAILURE'
        result={'status':'FAIL','reason':reason,'started_utc':started,'scenario':'browser-recovery','error':msg,'traceback':traceback.format_exc()}
    if args.report:
        out=Path(args.report);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
    if result['status']!='PASS':raise SystemExit(1)
