
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

function New-Archive {
    <#
    .SYNOPSIS
        Creates archive with built application.
    .DESCRIPTION
        Will create an archive with contents of 'dist' directory.
        Will add current application version to archive name and type of build.
        If current branch is 'master' type would be RELEASE otherwise SNAPSHOT.
    #>
    # Read version from JSON
    $version = (Get-Content -Raw ./config/main.json | ConvertFrom-Json).version

    # Get current Git branch
    $branch = git rev-parse --abbrev-ref HEAD

    # Determine type
    $type = if ($branch -eq 'master') { 'RELEASE' } else { 'SNAPSHOT' }

    # Create ZIP archive
    $buildsDir = "builds"
    $zipName = "$buildsDir/SaveGem-$version-$type.zip"

    # Create 'builds' directory if missing.
    if (-not (Test-Path $buildsDir)) {
        New-Item -ItemType Directory -Path $buildsDir | Out-Null
    }

    # Remove existing ZIP if exists
    if (Test-Path $zipName) {
        Remove-Item $zipName -Force
    }

    # Compress folder
    Compress-Archive -Path "dist/SaveGem" -DestinationPath $zipName
    Write-Host "Created archive: $zipName"
}
