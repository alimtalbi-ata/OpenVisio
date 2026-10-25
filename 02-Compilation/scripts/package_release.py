"""Produce a Windows cumulative ZIP only from freshly built artifacts.
Author: Abdelhalim Talbi.
"""
from pathlib import Path
from hashlib import sha256
import json
import zipfile

root = Path(__file__).resolve().parents[1]
project = root.parent
out = root / "dist"
portable = out / "OpenVisio-v42.7-Windows-x64-Portable.exe"
installer = out / "installer" / "OpenVisio-Setup-v42.7-x64.exe"
docs = [out / "documentation" / f"OpenVisio-v42.7-Guide-Windows.{ext}"
        for ext in ("docx", "pdf")]
required = [portable, installer, *docs]
for artifact in required:
    if not artifact.is_file() or artifact.stat().st_size < 1000:
        raise SystemExit(f"Missing real Windows artifact: {artifact}")

entries = {}
def add_file(source, archive_name):
    archive_name = str(archive_name).replace("\\", "/")
    if archive_name in entries:
        raise ValueError(f"Duplicate ZIP path: {archive_name}")
    entries[archive_name] = source.read_bytes()

for folder in ("02-Compilation", "03-Sources", "04-Tests", "05-Documentation", "06-Historique"):
    for source in sorted((project / folder).rglob("*")):
        if not source.is_file() or source.suffix in (".pyc", ".exe", ".zip"):
            continue
        if any(part in (".venv", "dist", "build", "__pycache__") for part in source.relative_to(project).parts):
            continue
        if folder == "02-Compilation" and source.name == "package_release.py":
            pass
        add_file(source, source.relative_to(project))
for source in (portable, installer):
    add_file(source, "01-Application/binary/" + source.name)
for source in docs:
    add_file(source, "05-Documentation/" + source.name)

entries["01-Application/BUILD-STATUS.txt"] = (
    "Real Windows binaries built in CI. Windows smoke and external Microsoft Visio "
    "fidelity are separate qualification gates.\\n"
).encode("utf-8")

# Cover every payload file in the manifest before serializing the manifest itself.
manifest = {
    "version": "42.7.0", "author": "Abdelhalim Talbi",
    "qualification": "windows-built; functional-fidelity-pending",
    "files": {name: {"sha256": sha256(data).hexdigest(), "bytes": len(data)}
              for name, data in sorted(entries.items())}
}
entries["07-Manifestes/manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
# The checksum list covers payload plus manifest; it intentionally excludes itself.
entries["07-Manifestes/SHA256SUMS.txt"] = "".join(
    f"{sha256(data).hexdigest()}  {name}\\n" for name, data in sorted(entries.items())
).encode("utf-8")
target = out / "OpenVisio-v42.7-Windows-Cumulative.zip"
with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for name, content in sorted(entries.items()):
        archive.writestr(name, content)
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None, "ZIP CRC validation failed"
    archive_names = set(archive.namelist())
    loaded_manifest = json.loads(archive.read("07-Manifestes/manifest.json"))
    for name, expected in loaded_manifest["files"].items():
        assert name in archive_names, f"Manifest entry missing from ZIP: {name}"
        payload = archive.read(name)
        assert len(payload) == expected["bytes"], f"Manifest size mismatch: {name}"
        assert sha256(payload).hexdigest() == expected["sha256"], f"Manifest SHA-256 mismatch: {name}"
    checksums = archive.read("07-Manifestes/SHA256SUMS.txt").decode("utf-8").splitlines()
    for line in checksums:
        digest, name = line.split("  ", 1)
        assert name in archive_names, f"Checksum entry missing from ZIP: {name}"
        assert sha256(archive.read(name)).hexdigest() == digest, f"Checksum mismatch: {name}"
    assert "01-Application/BUILD-STATUS.txt" in loaded_manifest["files"], "Build status is not manifest-covered"
print("Verified Windows ZIP, manifest and SHA-256 list:", target)
