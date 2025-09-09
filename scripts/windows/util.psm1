
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
