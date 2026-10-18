# OpenVisio v41.49 — Windows build hardening

Auteur : Abdelhalim Talbi

- Removed obsolete portable ZIP cleanup; portable single EXE remains target.
- Enforced portable EXE existence before success.
- Moved release manifest generation after both installer and portable publication.
- Updated package/.NET/Inno/CMD version to 41.49.
- Added static checks for build ordering and portable artifact.

Windows executables cannot be certified without executing the build on Windows.
