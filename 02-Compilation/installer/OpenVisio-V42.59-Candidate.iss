; OpenVisio V42.59 Windows candidate. Runtime version remains 42.50.0.
; Author: Abdelhalim Talbi. Qualification required before production use.
#define AppVersion "42.50.0"
[Setup]
AppId={{A7E490D2-1976-46CA-BFB8-CB80557D4E20}
AppName=OpenVisio
AppVersion={#AppVersion}
AppPublisher=Abdelhalim Talbi
DefaultDirName={autopf}\OpenVisio
DefaultGroupName=OpenVisio
OutputDir=..\..\dist\installer
OutputBaseFilename=OpenVisio-Setup-v42.59-Candidate-x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\OpenVisio.exe
[Files]
Source: "..\..\dist\OpenVisio-v42.59-Windows-x64-Portable.exe"; DestDir: "{app}"; DestName: "OpenVisio.exe"; Flags: ignoreversion
[Icons]
Name: "{group}\OpenVisio"; Filename: "{app}\OpenVisio.exe"
Name: "{autodesktop}\OpenVisio"; Filename: "{app}\OpenVisio.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Raccourci Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked
