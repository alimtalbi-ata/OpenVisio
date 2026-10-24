; OpenVisio V42.90 source candidate (internal app version 42.50.0).
; Author: Abdelhalim Talbi. Not a Microsoft Visio fidelity certificate.
#define AppVersion "42.50.0"
[Setup]
AppId={{A7E490D2-1976-46CA-BFB8-CB80557D4E20}
AppName=OpenVisio Source Candidate V42.90
AppVersion={#AppVersion}
AppPublisher=Abdelhalim Talbi
DefaultDirName={autopf}\OpenVisio
DefaultGroupName=OpenVisio
OutputDir=..\..\dist\installer
OutputBaseFilename=OpenVisio-V42.90-Source-Candidate-Setup-x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\OpenVisio.exe
[Files]
Source: "..\..\dist\OpenVisio-V42.90-Source-Candidate-Windows-x64-Portable.exe"; DestDir: "{app}"; DestName: "OpenVisio.exe"; Flags: ignoreversion
[Icons]
Name: "{group}\OpenVisio"; Filename: "{app}\OpenVisio.exe"
Name: "{autodesktop}\OpenVisio"; Filename: "{app}\OpenVisio.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Raccourci Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked
