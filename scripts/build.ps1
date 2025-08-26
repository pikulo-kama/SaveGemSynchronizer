function Assert-File-Exists {
    <#
    .SYNOPSIS
        Verifies that a file exists.
    .DESCRIPTION
        Checks if a file is present at the given path.
        Exits with an error if the file is missing.
    .PARAMETER Path
        Path to the file to check.
    .EXAMPLE
        Assert-File-Exists "file.txt"
    #>
    param(
        [string]$Path
    )

    if (-not (Test-Path $Path -PathType Leaf)) {
        Write-Host "ERROR: $Path not found!" -ForegroundColor Red
        exit 1
    }
}

# Check if configuration files are present.
Assert-File-Exists "credentials.json"
Assert-File-Exists "game-config-file-id.txt"

# Install dependencies
pip install -r requirements.txt
.\.venv\Scripts\activate.ps1

# Build executable with pyinstaller
pyinstaller --clean main.spec

# Remove EXE if exists
Remove-Item -Force "*.exe"

# Move built EXE from dist to current folder
Move-Item "dist\*.exe" "."

# Remove dist and build folders
Remove-Item -Recurse -Force dist, build
