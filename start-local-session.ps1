param(
    [string]$ApiHost = "127.0.0.1",
    [int]$ApiPort = 8000,
    [string]$FrontendHost = "127.0.0.1",
    [int]$FrontendPort = 5174,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiBaseUrl = "http://$ApiHost`:$ApiPort"
$apiHealth = "$apiBaseUrl/health"
$frontendUrl = "http://$FrontendHost`:$FrontendPort"

$pythonExe = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    throw "No se encontro .venv en $root. Crea/activa el entorno virtual primero."
}

# Ensure local frontend always points to local API
$envLocalPath = Join-Path $root "frontend\.env.local"
"VITE_API_URL=$apiBaseUrl" | Set-Content -Path $envLocalPath -Encoding ascii

$apiCommand = "Set-Location '$root'; & '$pythonExe' -m uvicorn api.app.main:app --host $ApiHost --port $ApiPort --reload"
$frontendCommand = "Set-Location '$root\\frontend'; npm run dev -- --host $FrontendHost --port $FrontendPort"

Start-Process pwsh -ArgumentList "-NoExit", "-Command", $apiCommand | Out-Null
Start-Sleep -Seconds 2
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $frontendCommand | Out-Null

$apiUp = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $status = (Invoke-WebRequest -Uri $apiHealth -UseBasicParsing -TimeoutSec 2).StatusCode
        if ($status -eq 200) {
            $apiUp = $true
            break
        }
    }
    catch {
    }
    Start-Sleep -Seconds 1
}

if (-not $NoBrowser) {
    Start-Process $frontendUrl | Out-Null
}

if ($apiUp) {
    Write-Host "Sesion local iniciada." -ForegroundColor Green
    Write-Host "API: $apiHealth"
    Write-Host "Frontend: $frontendUrl"
    Write-Host "VITE_API_URL: $apiBaseUrl"
    Write-Host "Usuario demo: analista.finanzas / demo123"
}
else {
    Write-Warning "Se lanzaron los procesos, pero la API no respondio en /health a tiempo. Revisa la ventana de API."
}
