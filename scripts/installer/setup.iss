
#include "helpers.iss"

#define RootPath "..\..\"

#define AppName "SaveGem"
#define Author "Artur Parkour"
#define AppExeName "SaveGem.exe"
#define AppVersion GetAppVersion(RootPath + "config\app.json")

#define WatchdogName "SaveGem Watchdog"
#define WatchdogExeName "SaveGemWatchdog.exe"

#define ProcessWatcherExeName "_SaveGemProcessWatcher.exe"
#define GDriveWatcherExeName "_SaveGemGDriveWatcher.exe"

[Setup]
; --- App Info ---
AppId=271448C6-303C-4B7F-924E-0170DD4C8560
AppName={#AppName}
UninstallDisplayName={#AppName}
AppPublisher={#Author}
AppVersion={#AppVersion}
SetupIconFile={#RootPath}resources\application.ico
DefaultDirName={pf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputBaseFilename={#AppName}Setup-{#AppVersion}-{#GetBuildType(RootPath)}
OutputDir={#RootPath}output\installers
DisableProgramGroupPage=no

; --- Installer Settings ---
Compression=lzma
SolidCompression=yes
AllowRootDirectory=yes

[Files]
; Copy everything from PyInstaller one dir output
Source: "{#RootPath}output\dist\{#AppName}\*"; \
    DestDir: "{app}"; \
    Flags: recursesubdirs
    
[Tasks]
Name: "desktopicon"; \
    Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"

Name: "startmenuicon"; \
    Description: "{cm:CreateStartMenuShortcut}"; \
    GroupDescription: "{cm:AdditionalIcons}"

[Icons]
; Start Menu shortcut
Name: "{group}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\_internal\resources\application.ico"; \
    Tasks: startmenuicon

; Desktop shortcut (user chooses in installer)
Name: "{commondesktop}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\_internal\resources\application.ico"; \
    Tasks: desktopicon
    
; Add process watcher launcher to startup.
Name: "{userstartup}\{#WatchdogName}"; \
    Filename: "{app}\{#WatchdogExeName}"; \
    IconFilename: "{app}\_internal\resources\application.ico"

[Run]
; Add option to start application after installation.
Filename: "{app}\{#AppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent

; Start SaveGem Watchdog automatically after installation.
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    Exec(ExpandConstant('{app}\{#WatchdogExeName}'), '', '', SW_HIDE, ewNoWait, ResultCode);
  end;
end;

[UninstallRun]
; Kill main application.
Filename: "taskkill"; \
    Parameters: "/f /im {#AppExeName}"; \
    Flags: runhidden

; Kill watchdog.
Filename: "taskkill"; \
    Parameters: "/f /im {#WatchdogExeName}"; \
    Flags: runhidden

; Kill Google Drive watcher.
Filename: "taskkill"; \
    Parameters: "/f /im {#GDriveWatcherExeName}"; \
    Flags: runhidden

; Kill process watcher.
Filename: "taskkill"; \
    Parameters: "/f /im {#ProcessWatcherExeName}"; \
    Flags: runhidden
    
[UninstallDelete]
; Remove installation directory if it's empty.
Type: dirifempty; \
    Name: "{app}"

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "uk"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[CustomMessages]
en.CreateStartMenuShortcut=Create a Start Menu shortcut
uk.CreateStartMenuShortcut=Створити ярлик у меню Пуск

