; OpenVisio native Python Windows installer. Author: Abdelhalim Talbi.
#define AppVersion "42.7.0"
[Setup]
AppId={{A7E490D2-1976-46CA-BFB8-CB80557D4E20}
AppName=OpenVisio
AppVersion={#AppVersion}
AppPublisher=Abdelhalim Talbi
DefaultDirName={autopf}\OpenVisio
DefaultGroupName=OpenVisio
OutputDir=..\dist\installer
OutputBaseFilename=OpenVisio-Setup-v42.7-x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\OpenVisio.exe
[Files]
Source: "..\dist\OpenVisio-v42.7-Windows-x64-Portable.exe"; DestDir: "{app}"; DestName: "OpenVisio.exe"; Flags: ignoreversion
[Icons]
Name: "{group}\OpenVisio"; Filename: "{app}\OpenVisio.exe"
Name: "{autodesktop}\OpenVisio"; Filename: "{app}\OpenVisio.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Raccourci Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked
[Registry]
Root: HKA; Subkey: "Software\Classes\.ovjson"; ValueType: string; ValueData: "OpenVisio.Document"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\OpenVisio.Document"; ValueType: string; ValueData: "Document OpenVisio"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\OpenVisio.Document\shell\open\command"; ValueType: string; ValueData: """{app}\OpenVisio.exe"" ""%1"""
[Run]
Filename: "{app}\OpenVisio.exe"; Description: "Lancer OpenVisio"; Flags: nowait postinstall skipifsilent
