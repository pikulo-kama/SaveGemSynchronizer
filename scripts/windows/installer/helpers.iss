
; --------------------------------------------------------
; GetAppVersion(FileName)
; --------------------------------------------------------
; Reads a JSON file (e.g. config\main.json) and extracts
; the "version" field using PowerShell.
;
; Parameters:
;   FileName - Path to the JSON file.
;
; Returns:
;   The value of "version", e.g. "1.2.3".
;
; Example:
;   AppVersion={#GetAppVersion("config\main.json")}
;   → AppVersion=1.2.3
;
#define GetAppVersion(str fileName) \
  Local[0] = AddBackslash(GetEnv("TEMP")) + "version.txt", \
  Local[1] = \
    "-ExecutionPolicy Bypass -Command """ + \
    "$json = Get-Content '" + FileName + "' | ConvertFrom-Json;" + \
    "Set-Content -Path '" + Local[0] + "' -Value $json.version;" + \
    """", \
  Exec("powershell.exe", Local[1], SourcePath, , SW_HIDE), \
  Local[2] = FileOpen(Local[0]), \
  Local[3] = FileRead(Local[2]), \
  FileClose(Local[2]), \
  DeleteFileNow(Local[0]), \
  Local[3]


; --------------------------------------------------------
; GetBuildType(RepoPath)
; --------------------------------------------------------
; Uses Git to detect the current branch of a repository.
; If branch is "master" → returns "RELEASE"
; Otherwise → returns "SNAPSHOT".
;
; Parameters:
;   RepoPath - Path to the Git repository.
;
; Returns:
;   "RELEASE" or "SNAPSHOT".
;
; Example:
;   {#GetBuildType(".")}
;   → "RELEASE"  (if on master)
;   → "SNAPSHOT" (otherwise)
;
#define GetBuildType(str RepoPath) \
  Local[0] = AddBackslash(GetEnv("TEMP")) + "buildType.txt", \
  Local[1] = \
    "-ExecutionPolicy Bypass -Command """ + \
    "$branch = (git -C '" + RepoPath + "' rev-parse --abbrev-ref HEAD);" + \
    "if ($branch -eq 'master') { $type = 'RELEASE' } else { $type = 'SNAPSHOT' };" + \
    "Set-Content -Path '" + Local[0] + "' -Value $type;" + \
    """", \
  Exec("powershell.exe", Local[1], SourcePath, , SW_HIDE), \
  Local[2] = FileOpen(Local[0]), \
  Local[3] = FileRead(Local[2]), \
  FileClose(Local[2]), \
  DeleteFileNow(Local[0]), \
  Local[3]
