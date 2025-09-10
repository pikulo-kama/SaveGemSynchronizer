
#include "helpers.iss"
#define RootPath "..\..\"

[Setup]
; --- App Info ---
AppName=SaveGem
UninstallDisplayName=SaveGem
AppPublisher=Artur Parkour
AppVersion={#GetAppVersion(RootPath + "config\main.json")}
SetupIconFile={#RootPath}resources\application.ico
DefaultDirName={pf}\SaveGem
DefaultGroupName=SaveGem
UninstallDisplayIcon={app}\SaveGem.exe
OutputBaseFilename=SaveGemSetup-{#GetAppVersion(RootPath + "config\main.json")}-{#GetBuildType(RootPath)}
OutputDir={#RootPath}output\installers
DisableProgramGroupPage=no

; --- Installer Settings ---
Compression=lzma
SolidCompression=yes
AllowRootDirectory=yes

[Files]
; Copy everything from PyInstaller one dir output
Source: "{#RootPath}output\dist\SaveGem\*"; DestDir: "{app}"; Flags: recursesubdirs

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\SaveGem"

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM ProcessWatcher.exe"; Flags: runhidden

[Icons]
; Add watcher service to startup
Name: "{userstartup}\SaveGem Process Watcher"; Filename: "{app}\ProcessWatcher.exe"

; Start Menu shortcut
Name: "{group}\SaveGem"; Filename: "{app}\SaveGem.exe"; IconFilename: "{app}\_internal\resources\application.ico"

; Desktop shortcut (user chooses in installer)
Name: "{commondesktop}\SaveGem"; Filename: "{app}\SaveGem.exe"; IconFilename: "{app}\_internal\resources\application.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIconsGroup}"
Name: "startmenuicon"; Description: "{cm:CreateStartMenuShortcut}"; GroupDescription: "{cm:AdditionalIconsGroup}"

[Run]
; Add option to start application after installation.
Filename: "{app}\SaveGem.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent

; Start ProcessWatcher automatically after installation.
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    Exec(ExpandConstant('{app}\ProcessWatcher.exe'), '', '', SW_HIDE, ewNoWait, ResultCode);
  end;
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[CustomMessages]
english.AdditionalIconsGroup=Additional icons:
english.CreateDesktopIcon=Create a desktop icon
english.CreateStartMenuShortcut=Create a Start Menu shortcut
english.LaunchApp=Launch SaveGem
ukrainian.AdditionalIconsGroup=Додаткові значки:
ukrainian.CreateDesktopIcon=Створити значок на робочому столі
ukrainian.CreateStartMenuShortcut=Створити ярлик у меню Пуск
ukrainian.LaunchApp=Запустити SaveGem

