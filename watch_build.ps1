$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$watchPaths = @(
    (Join-Path $PSScriptRoot "src"),
    (Join-Path $PSScriptRoot "assets"),
    (Join-Path $PSScriptRoot "README.md"),
    (Join-Path $PSScriptRoot "README_EN.md"),
    (Join-Path $PSScriptRoot "AGENTS.md"),
    (Join-Path $PSScriptRoot "requirements.txt")
)

$watchers = @()
$pendingBuild = $false
$lastEventAt = Get-Date

function Invoke-Rebuild {
    Write-Host ""
    Write-Host ("[{0}] Rebuilding KeyboardPet.exe ..." -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
    try {
        & (Join-Path $PSScriptRoot "build_exe.ps1")
        Write-Host ("[{0}] Build finished." -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
    } catch {
        Write-Host ("[{0}] Build failed: {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $_.Exception.Message)
    }
}

foreach ($path in $watchPaths) {
    $isDirectory = Test-Path $path -PathType Container
    $directory = if ($isDirectory) { $path } else { Split-Path -Parent $path }
    $filter = if ($isDirectory) { "*.*" } else { Split-Path -Leaf $path }

    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $directory
    $watcher.Filter = $filter
    $watcher.IncludeSubdirectories = $isDirectory
    $watcher.EnableRaisingEvents = $true
    $watchers += $watcher

    $action = {
        if ($Event.SourceEventArgs.FullPath -like "*\assets\vocab\word_banks.json") {
            return
        }
        $script:pendingBuild = $true
        $script:lastEventAt = Get-Date
    }

    Register-ObjectEvent -InputObject $watcher -EventName Changed -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Created -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Renamed -Action $action | Out-Null
    Register-ObjectEvent -InputObject $watcher -EventName Deleted -Action $action | Out-Null
}

Write-Host "Watching project files for changes."
Write-Host "Press Ctrl+C to stop."

while ($true) {
    Start-Sleep -Milliseconds 500
    if ($pendingBuild -and ((Get-Date) - $lastEventAt).TotalSeconds -ge 1.5) {
        $pendingBuild = $false
        Invoke-Rebuild
    }
}
