
#include "helpers.iss"

#define AppName GetProperty("config\app.json", "name")
#define Author GetProperty("config\app.json", "author")
#define AppExeName GetProperty("config\app.json", "processName")
#define AppVersion GetProperty("config\app.json", "version")

#define WatchdogName GetProperty("config\watchdog.json", "name")
#define WatchdogExeName GetProperty("config\watchdog.json", "processName")

#define ProcessWatcherExeName GetProperty("config\process_watcher.json", "processName")
#define GDriveWatcherExeName GetProperty("config\gdrive_watcher.json", "processName")

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
OutputBaseFilename={#AppName}Setup-{#AppVersion}-{#GetBuildType()}
OutputDir={#RootPath}output\installers
DisableProgramGroupPage=no
CloseApplications=force

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

; Copy local logback to AppData if missing
Source: "{#RootPath}config\logback.json"; \
    DestDir: "{userappdata}\{#AppName}"; \
    DestName: "logback.json"; \
    Flags: ignoreversion
    
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
    
; Add watchdog to startup.
Name: "{userstartup}\{#WatchdogName}"; \
    Filename: "{app}\{#WatchdogExeName}"; \
    IconFilename: "{app}\_internal\resources\application.ico"

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

; Add option to start application after installation.
Filename: "{app}\{#AppExeName}"; \
    Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; \
    Flags: nowait postinstall skipifsilent

; ------------------------------------------------------------------------- ;
; UNINSTALL SECTION
; ------------------------------------------------------------------------- ;

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
en.RemoveUserDataPrompt=Do you want to remove all %1 user data?

uk.CreateStartMenuShortcut=Створити ярлики у меню Пуск
uk.RemoveUserDataPrompt=Бажаєте видалити всі дані користувача %1?

fr.CreateStartMenuShortcut=Créer un raccourci dans le menu Démarrer
fr.RemoveUserDataPrompt=Voulez-vous supprimer toutes les données utilisateur de %1?

de.CreateStartMenuShortcut=Verknüpfung im Startmenü erstellen
de.RemoveUserDataPrompt=Möchten Sie alle Benutzerdaten von %1 löschen?

es.CreateStartMenuShortcut=Crear un acceso directo en el menú Inicio
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
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Prompt: String;
begin

  if CurUninstallStep = usUninstall then
  begin
    Prompt := FmtMessage(CustomMessage('RemoveUserDataPrompt'), ['{#AppName}'])

    if MsgBox(Prompt, mbConfirmation, MB_YESNO) = IDYES then
      DelTree(ExpandConstant('{userappdata}\{#AppName}'), True, True, True);
  end;
end;
