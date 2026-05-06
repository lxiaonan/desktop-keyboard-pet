$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip pyinstaller pystray Pillow
.\.venv\Scripts\pyinstaller.exe --noconsole --onefile --name KeyboardPet --add-data "assets;assets" src\keyboard_pet.py

Write-Host ""
Write-Host "Done. EXE: $PSScriptRoot\dist\KeyboardPet.exe"
