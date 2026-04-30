# Build the standalone Windows exe via PyInstaller.
# Run from the repo root in PowerShell:  .\build.ps1
# Output: dist\greenshot-to-punchlist.exe

$ErrorActionPreference = "Stop"

if (-not (Test-Path .\.venv)) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

$iconArg = @()
if (Test-Path .\greenshot_to_punchlist\resources\icon.ico) {
    $iconArg = @("--icon", ".\greenshot_to_punchlist\resources\icon.ico")
}

.\.venv\Scripts\pyinstaller.exe `
    --onefile `
    --noconsole `
    --name greenshot-to-punchlist `
    @iconArg `
    .\greenshot_to_punchlist\__main__.py

Write-Host ""
Write-Host "Built: $(Resolve-Path .\dist\greenshot-to-punchlist.exe)"
Write-Host "Drop the exe and config.example.json (renamed to config.json) into the same folder."
