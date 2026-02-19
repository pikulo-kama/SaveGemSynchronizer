
#include "helpers.iss"

#define AppName GetProperty("serviceInfo\app.json", "name")
#define Author GetProperty("serviceInfo\app.json", "author")
#define AppExeName GetProperty("serviceInfo\app.json", "processName")
#define AppVersion GetProperty("serviceInfo\app.json", "version")

#define WatchdogName GetProperty("serviceInfo\watchdog.json", "name")
#define WatchdogExeName GetProperty("serviceInfo\watchdog.json", "processName")

#define ProcessWatcherExeName GetProperty("serviceInfo\process_watcher.json", "processName")
#define GDriveWatcherExeName GetProperty("serviceInfo\gdrive_watcher.json", "processName")
#define KamaDbmExeName GetProperty("serviceInfo\kama-dbm.json", "processName")


[Setup]
; --- App Info ---
AppId=271448C6-303C-4B7F-924E-0170DD4C8560
AppName={#AppName}
UninstallDisplayName={#AppName}
AppPublisher={#Author}
AppVersion={#AppVersion}
SetupIconFile={#RootPath}resources\images\application.ico
DefaultDirName={commonpf}\{#AppName}
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
OutputBaseFilename={#AppName}Setup-{#AppVersion}-{#GetBuildType()}
OutputDir={#RootPath}output\installers
DisableProgramGroupPage=no
CloseApplications=force
UsedUserAreasWarning=no

; --- Installer Settings ---
Compression=lzma
SolidCompression=yes
AllowRootDirectory=yes

; ------------------------------------------------------------------------- ;
; INSTALL SECTION
; ------------------------------------------------------------------------- ;

[Dirs]
; AppData root
Name: "{userappdata}\{#AppName}"

; Output dir
Name: "{userappdata}\{#AppName}\Output"

; Logs dir
Name: "{userappdata}\{#AppName}\Logs"

[Files]
; Copy everything from PyInstaller one dir output
Source: "{#RootPath}output\dist\{#AppName}\*"; \
    DestDir: "{app}"; \
    Flags: recursesubdirs replacesameversion

; Copy local logback files to AppData
Source: "{#RootPath}logback\*"; \
    DestDir: "{userappdata}\{#AppName}\Logback"; \
    Flags: ignoreversion

; Install Fonts
Source: "{#RootPath}fonts\PT_Sans_Caption\PTSansCaption-Regular.ttf"; \
    DestDir: "{autofonts}"; \
    FontInstall: "PT Sans Caption"; \
    Flags: onlyifdoesntexist uninsneveruninstall

Source: "{#RootPath}fonts\Plus_Jakarta_Sans\PlusJakartaSans-Regular.ttf"; \
    DestDir: "{autofonts}"; \
    FontInstall: "Plus Jakarta Sans"; \
    Flags: onlyifdoesntexist uninsneveruninstall

Source: "{#RootPath}fonts\Plus_Jakarta_Sans\PlusJakartaSans-ExtraBold.ttf"; \
    DestDir: "{autofonts}"; \
    FontInstall: "Plus Jakarta Sans ExtraBold"; \
    Flags: onlyifdoesntexist uninsneveruninstall
    
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
    IconFilename: "{app}\_internal\resources\images\application.ico"; \
    Tasks: startmenuicon

; Desktop shortcut (user chooses in installer)
Name: "{commondesktop}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    IconFilename: "{app}\_internal\resources\images\application.ico"; \
    Tasks: desktopicon
    
; Add watchdog to startup.
Name: "{userstartup}\{#WatchdogName}"; \
    Filename: "{app}\{#WatchdogExeName}"; \
    IconFilename: "{app}\_internal\resources\images\application.ico"

[Run]
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

Filename: "schtasks"; \
    Parameters: "/Create /TN ""SaveGemWatchdog"" /TR ""'{app}\{#WatchdogExeName}'"" /SC ONLOGON /RL HIGHEST /F"; \
    Flags: runhidden; \
    StatusMsg: "Configuring startup settings..."

; ------------------------------------------------------------------------- ;
; UNINSTALL SECTION
; ------------------------------------------------------------------------- ;

[UninstallRun]
; Kill main application.
Filename: "taskkill"; \
    RunOnceId: "KillApplication"; \
    Parameters: "/f /im {#AppExeName}"; \
    Flags: runhidden

; Kill watchdog.
Filename: "taskkill"; \
    RunOnceId: "KillWatchdog"; \
    Parameters: "/f /im {#WatchdogExeName}"; \
    Flags: runhidden

; Kill Google Drive watcher.
Filename: "taskkill"; \
    RunOnceId: "KillGoogleDriveWatcher"; \
    Parameters: "/f /im {#GDriveWatcherExeName}"; \
    Flags: runhidden

; Kill process watcher.
Filename: "taskkill"; \
    RunOnceId: "KillProcessWatcher"; \
    Parameters: "/f /im {#ProcessWatcherExeName}"; \
    Flags: runhidden
    
Filename: "schtasks"; \
    RunOnceId: "UnscheduleWatchdog"; \
    Parameters: "/Delete /TN ""SaveGemWatchdog"" /F"; \
    Flags: runhidden
    
[UninstallDelete]
; Remove installation directory if it's empty.
Type: dirifempty; \
    Name: "{app}"

; ------------------------------------------------------------------------- ;
; LANGUAGES SECTION
; ------------------------------------------------------------------------- ;

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "uk"; MessagesFile: "compiler:Languages\Ukrainian.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
en.CreateStartMenuShortcut=Create a Start Menu shortcut
uk.CreateStartMenuShortcut=Створити ярлики у меню Пуск
fr.CreateStartMenuShortcut=Créer un raccourci dans le menu Démarrer
de.CreateStartMenuShortcut=Verknüpfung im Startmenü erstellen
es.CreateStartMenuShortcut=Crear un acceso directo en el menú Inicio

en.RemoveUserDataPrompt=Do you want to remove all %1 user data?
uk.RemoveUserDataPrompt=Бажаєте видалити всі дані користувача %1?
fr.RemoveUserDataPrompt=Voulez-vous supprimer toutes les données utilisateur de %1?
de.RemoveUserDataPrompt=Möchten Sie alle Benutzerdaten von %1 löschen?
es.RemoveUserDataPrompt=¿Desea eliminar todos los datos de usuario de %1?

; ------------------------------------------------------------------------- ;
; CODE SECTION
; ------------------------------------------------------------------------- ;

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
    // Immediately start watchdog process.
    Exec(ExpandConstant('{app}\{#WatchdogExeName}'), '', '', SW_HIDE, ewNoWait, ResultCode);
    
    // Migrate database schema changes.
    Exec(ExpandConstant('{app}\{#KamaDbmExeName}'), ExpandConstant('migrate --migration_directories="{app}/_internal/migration" --database="{userappdata}/{#AppName}/savegem.db"'), '', SW_HIDE, ewNoWait, ResultCode);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Prompt: String;
  PowerShellCmd: String;
  ResultCode: Integer;
begin

  if CurUninstallStep = usUninstall then
  begin
    Prompt := FmtMessage(CustomMessage('RemoveUserDataPrompt'), ['{#AppName}'])

    if MsgBox(Prompt, mbConfirmation, MB_YESNO) = IDYES then
      DelTree(ExpandConstant('{userappdata}\{#AppName}'), True, True, True);
      
      // Remove credentials from credential manager.
      PowerShellCmd := 'cmdkey /list | ForEach-Object { if ($_ -match ''Target: (LegacyGeneric:target={#AppName})$'') { cmdkey /delete:($Matches[1]) } }';
      Exec('powershell.exe', '-WindowStyle Hidden -Command "' + PowerShellCmd + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
