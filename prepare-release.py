#!/usr/bin/env python3
"""OpenVisio cumulative release gate: stdlib only. Run from release root."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile,os,tempfile
ROOT=Path(__file__).resolve().parent
VERSION="41.8"
SECTIONS=["01-LIRE-EN-PREMIER","02-UTILISATION","03-INSTALLATION","04-COMPILATION","05-ARCHITECTURE","06-QUALIFICATION","07-CAPTURES"]
def gate(skip_tests=False,output=None):
 app=ROOT/"application";docs=ROOT/"documentation"; manifest=ROOT/"manifest"
 assert json.loads((app/"package.json").read_text())["version"]=="41.0.0", "Base applicative attendue 41.0.0"
 assert (app/"index.html").is_file() and (app/"src/main.js").is_file(),"Sources manquantes"
 for section in SECTIONS:
  folder=docs/section
  for ext in ("md","docx","pdf"):
   target=folder/("README.md" if ext=="md" else f"Guide-v{VERSION}.{ext}")
   assert target.is_file() and target.stat().st_size>100, f"Document absent/vide: {target}"
  assert (folder/f"Guide-v{VERSION}.pdf").read_bytes().startswith(b"%PDF"),"PDF invalide"
  assert (folder/f"Guide-v{VERSION}.docx").read_bytes().startswith(b"PK"),"DOCX invalide"
 assert (docs/"07-CAPTURES"/"STATUT-CAPTURES.md").is_file(),"Statut captures manquant"
 capture_status=(docs/"07-CAPTURES"/"STATUT-CAPTURES.md").read_text(encoding="utf-8")
 assert "non disponibles" in capture_status.lower() or "capture" in capture_status.lower(),"Statut captures non explicite"
 if output and skip_tests: raise RuntimeError("Publication interdite avec --skip-tests")
 if not skip_tests:
  proc=subprocess.run(["node","--test",*sorted(str(p.relative_to(app)) for p in (app/"tests").glob("*.test.mjs"))],cwd=app,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  print(proc.stdout[-2500:]);assert proc.returncode==0,"Tests Node.js échoués"
 files=sorted(p for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p!=output and p!=manifest/"files-sha256.json")
 hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 manifest.mkdir(exist_ok=True);(manifest/"files-sha256.json").write_text(json.dumps({"version":VERSION,"files":hashes},indent=2,ensure_ascii=False)+"\n")
 files.append(manifest/"files-sha256.json")
 if output:
  with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
   for p in sorted(files):z.write(p,ROOT.name+"/"+str(p.relative_to(ROOT)))
  with zipfile.ZipFile(output) as z:
   assert z.testzip() is None,"ZIP corrompu"
   for name,digest in hashes.items():
    actual=hashlib.sha256(z.read(ROOT.name+"/"+name)).hexdigest()
    assert actual==digest,f"ZIP: empreinte incorrecte {name}"
   assert len(z.namelist())==len(files),"ZIP: nombre de fichiers incoherent"
 print(f"PASS version={VERSION} files={len(files)} output={output}")
if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--skip-tests",action="store_true",help="Diagnostic uniquement, ne pas utiliser pour publier");parser.add_argument("--output",type=Path)
 a=parser.parse_args();gate(a.skip_tests,a.output)
