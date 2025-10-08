<#
PowerShell setup helper for Windows users.
Usage:
  Open PowerShell (run as Administrator if you expect to need serial device permissions) and run:
    .\dev-setup.ps1 -Target all
  Or for just the launcher:
    .\dev-setup.ps1 -Target launcher
#>
param(
    [ValidateSet('all','launcher','tracker')]
    [string]$Target = 'all'
)

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Dev setup root: $ScriptRoot"

function Setup-App($AppRelPath) {
    $AppPath = Join-Path $ScriptRoot $AppRelPath
    if (-not (Test-Path $AppPath)) {
        Write-Error "App path not found: $AppPath"; return
    }
    Push-Location $AppPath
    $venvPath = Join-Path $AppPath ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating venv for $AppRelPath..."
        py -3 -m venv $venvPath
    } else {
        Write-Host "Using existing venv at $venvPath"
    }

    $venvPython = Join-Path $venvPath "Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Error "Python executable not found in venv: $venvPython"; Pop-Location; return
    }

    Write-Host "Upgrading pip and installing requirements for $AppRelPath..."
    & $venvPython -m pip install -U pip setuptools wheel
    if (Test-Path "requirements.txt") {
        & $venvPython -m pip install -r requirements.txt
    }

    Pop-Location
}

switch ($Target) {
    'launcher' { Setup-App 'Applications\\Launcher' }
    'tracker'  { Setup-App 'Applications\\HandTracker' }
    'all'      { Setup-App 'Applications\\Launcher'; Setup-App 'Applications\\HandTracker' }
}

Write-Host "Done. To run the launcher (Windows):"
Write-Host "  .\Applications\Launcher\.venv\Scripts\python.exe .\Applications\Launcher\launcher.py"
Write-Host "Or open PowerShell and run:`n  Set-Location .\Applications\Launcher` then:`n  .\.venv\Scripts\Activate.ps1` and `python launcher.py`"
