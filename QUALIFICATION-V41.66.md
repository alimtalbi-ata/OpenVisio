# OpenVisio v41.66 — Recovery state-machine scenarios

Auteur : Abdelhalim Talbi

Adds isolated synthetic checkpoint restoration, post-restore verification and refusal to overwrite a valid binary release. Synthetic MZ fixtures are **not runnable Windows executables** and are never shipped as precompiled binaries. The PowerShell scenarios have not been run on Windows in this environment.

Run on Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File .\windows\Test-Binary-Recovery-Scenarios.ps1 -ReportPath .\qualification\recovery-v41.66.json`

Node.js test suite: 1833 PASS / 1843, 10 FAIL. NOT QUALIFIED. See TESTS-V41.66.log. No native Windows binaries were built; no PowerShell scenarios were executed. Documentation Word/PDF v41.66 has not been updated.
