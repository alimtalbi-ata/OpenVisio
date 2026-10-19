"""Create reproducible cumulative release ZIP with real artifacts only."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
portable = dist / "OpenVisio-v42.1-Windows-x64-Portable.exe"
installer = dist / "installer" / "OpenVisio-Setup-v42.1-x64.exe"
docs = [dist / "documentation" / f"OpenVisio-v42.1-Guide-Windows.{ext}" for ext in ("docx", "pdf")]
required = [portable, installer, *docs]
for file in required:
    if not file.is_file() or file.stat().st_size < 1000:
        raise SystemExit(f"Missing or invalid release artifact: {file}")
binary = root / "binary"
binary.mkdir(exist_ok=True)
for file in (portable, installer):
    (binary / file.name).write_bytes(file.read_bytes())
manifest = {"version": "42.1.0", "author": "Abdelhalim Talbi", "status": "built-not-qualified-on-clean-PC", "artifacts": [
    {"name": p.name, "size": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in required]}
(binary / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
target = dist / "OpenVisio-v42.1-Windows-Cumulative.zip"
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
    for file in sorted((root / "openvisio").rglob("*.py")):
        archive.write(file, "03-Sources/" + str(file.relative_to(root)))
    for file in sorted((root / "tests").rglob("*.py")):
        archive.write(file, "04-Tests/" + str(file.relative_to(root)))
    for file in [root / "Build-Windows.cmd", root / "installer/OpenVisio-Python.iss", root / "requirements-build.txt", root / "README.md"]:
        archive.write(file, "02-Compilation/" + str(file.relative_to(root)))
    for file in sorted((root / "docs").rglob("*.md")):
        archive.write(file, "05-Documentation/technique/" + file.name)
    for file in (portable, installer):
        archive.write(file, "01-Application/binary/" + file.name)
    for file in docs:
        archive.write(file, "05-Documentation/" + file.name)
    archive.write(binary / "manifest.json", "07-Manifestes/manifest.json")
    archive.write(root / "run_openvisio.py", "03-Sources/run_openvisio.py")
    for script in ("generate_docs.py", "package_release.py"):
        archive.write(root / "scripts" / script, "02-Compilation/scripts/" + script)
    for script in ("Smoke-Portable-Windows.ps1", "Smoke-Installer-Windows.ps1"):
        archive.write(root / "scripts" / script, "04-Tests/" + script)
    archive.writestr("06-Historique/README.txt", "OpenVisio 42.1.0 - Auteur : Abdelhalim Talbi\nCommits : https://github.com/alimtalbi-ata/OpenVisio/commits/develop/openvisio-python-v42/\nQualification : CI Windows ; installation PC tiers non certifiee.\n")
with zipfile.ZipFile(target) as archive:
    if archive.testzip() is not None:
        raise SystemExit("ZIP integrity check failed")
print(target)
