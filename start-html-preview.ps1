param(
    [int]$Port = 8080
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    $pythonExe = 'python'
}

$serverUrl = "http://127.0.0.1:$Port/index.html"

Push-Location $root
try {
    Start-Process -FilePath $pythonExe -ArgumentList '-m','http.server',$Port -WorkingDirectory $root | Out-Null
    Start-Sleep -Seconds 2
    Start-Process $serverUrl | Out-Null
    Write-Host "Vista previa lista en $serverUrl" -ForegroundColor Green
    Write-Host "Abre directamente la URL o usa el index para navegar entre vistas." -ForegroundColor Cyan
}
finally {
    Pop-Location
}
