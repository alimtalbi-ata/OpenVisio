; OpenVisio Windows installer. Author: Abdelhalim Talbi.
#define AppVersion "41.70.0"
[Setup]
AppId={{A7E490D2-1976-46CA-BFB8-CB80557D4E20}
AppName=OpenVisio
AppVersion={#AppVersion}
AppPublisher=Abdelhalim Talbi
DefaultDirName={autopf}\OpenVisio
DefaultGroupName=OpenVisio
OutputDir=..\..\dist\installer
OutputBaseFilename=OpenVisio-Setup-v41.70-x64
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
SetupLogging=yes
ChangesAssociations=yes
UninstallDisplayIcon={app}\OpenVisio.exe
[Files]
Source: "..\..\dist\prerequisites\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "..\..\dist\windows-x64\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\OpenVisio"; Filename: "{app}\OpenVisio.exe"
Name: "{autodesktop}\OpenVisio"; Filename: "{app}\OpenVisio.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"; Flags: unchecked
[Registry]
Root: HKA; Subkey: "Software\Classes\.ovjson"; ValueType: string; ValueName: ""; ValueData: "OpenVisio.Document"; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\OpenVisio.Document"; ValueType: string; ValueName: ""; ValueData: "Document OpenVisio"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\OpenVisio.Document\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\OpenVisio.exe"" ""%1"""

[Run]
Filename: "{tmp}\MicrosoftEdgeWebView2RuntimeInstallerX64.exe"; Parameters: "/silent /install"; StatusMsg: "Installation de Microsoft Edge WebView2 Runtime..."; Flags: waituntilterminated runhidden; Check: not HasWebView2
Filename: "{app}\OpenVisio.exe"; Description: "Démarrer OpenVisio"; Flags: nowait postinstall skipifsilent; Check: HasWebView2

[Code]
function HasWebView2: Boolean;
var V: String;
begin
 Result := RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F1E7E12B-9D1B-4A31-8E4C-8CF9D8B8B3B9}', 'pv', V) or
           RegQueryStringValue(HKCU, 'Software\Microsoft\EdgeUpdate\Clients\{F1E7E12B-9D1B-4A31-8E4C-8CF9D8B8B3B9}', 'pv', V);
 Result := Result and (V <> '') and (V <> '0.0.0.0');
end;
