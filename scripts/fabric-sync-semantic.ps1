param(
    [Parameter(Mandatory = $false)]
    [string]$ApiBaseUrl = "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io",

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId,

    [Parameter(Mandatory = $true)]
    [string]$DatasetId,

    [Parameter(Mandatory = $false)]
    [string]$TableName = "DashboardPayload",

    [Parameter(Mandatory = $false)]
    [string]$AdminUser = "admin.valuehub",

    [Parameter(Mandatory = $false)]
    [string]$AdminPassword = "Demo1234!",

    [Parameter(Mandatory = $false)]
    [string]$Period = "current"
)

$ErrorActionPreference = "Stop"

function Get-PowerBIToken {
    $tokenJson = az account get-access-token --resource https://analysis.windows.net/powerbi/api --output json | ConvertFrom-Json
    if (-not $tokenJson.accessToken) {
        throw "No se pudo obtener token de Power BI/Fabric API"
    }
    return $tokenJson.accessToken
}

function Invoke-PbiApi {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Method,
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $false)]
        [object]$Body = $null
    )

    $token = Get-PowerBIToken
    $uri = "https://api.powerbi.com/v1.0/myorg/$Path"
    $headers = @{ Authorization = "Bearer $token" }

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers
    }

    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 30)
}

Write-Host "Obteniendo snapshot de dashboard desde API..." -ForegroundColor Cyan
$loginBody = @{ username = $AdminUser; password = $AdminPassword } | ConvertTo-Json
$auth = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/auth/login" -ContentType "application/json" -Body $loginBody
$apiHeaders = @{ Authorization = "Bearer $($auth.access_token)" }
$dashboard = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/admin/metrics/executive-dashboard/snapshot?period=$Period" -Headers $apiHeaders

$tenantId = $dashboard.tenant_id
$generatedAt = (Get-Date).ToUniversalTime().ToString("o")
$payloadJson = $dashboard | ConvertTo-Json -Depth 50 -Compress

Write-Host "Limpiando tabla semantica '$TableName'..." -ForegroundColor Cyan
Invoke-PbiApi -Method DELETE -Path "groups/$WorkspaceId/datasets/$DatasetId/tables/$TableName/rows"

Write-Host "Insertando nuevo payload semantico..." -ForegroundColor Cyan
$rowsBody = @{
    rows = @(
        @{
            tenant_id = $tenantId
            period = $Period
            generated_at = $generatedAt
            payload_json = $payloadJson
        }
    )
}

Invoke-PbiApi -Method POST -Path "groups/$WorkspaceId/datasets/$DatasetId/tables/$TableName/rows" -Body $rowsBody

Write-Host "Sincronizacion completada." -ForegroundColor Green
Write-Host "tenant_id=$tenantId | period=$Period | generated_at=$generatedAt"
