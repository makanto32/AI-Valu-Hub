param(
    [Parameter(Mandatory = $false)]
    [string]$WorkspaceName = "latamdemos",

    [Parameter(Mandatory = $false)]
    [string]$DatasetName = "AIHubSemanticModel",

    [Parameter(Mandatory = $false)]
    [string]$TableName = "DashboardPayload"
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

    return Invoke-RestMethod -Method $Method -Uri $uri -Headers $headers -ContentType "application/json" -Body ($Body | ConvertTo-Json -Depth 20)
}

Write-Host "Buscando workspace '$WorkspaceName'..." -ForegroundColor Cyan
$groups = Invoke-PbiApi -Method GET -Path "groups"
$workspace = $groups.value | Where-Object { $_.name -eq $WorkspaceName } | Select-Object -First 1

if (-not $workspace) {
    throw "No se encontro workspace '$WorkspaceName' en el tenant actual"
}

$workspaceId = $workspace.id
Write-Host "Workspace encontrado: $WorkspaceName ($workspaceId)" -ForegroundColor Green

Write-Host "Buscando dataset '$DatasetName'..." -ForegroundColor Cyan
$datasets = Invoke-PbiApi -Method GET -Path "groups/$workspaceId/datasets"
$dataset = $datasets.value | Where-Object { $_.name -eq $DatasetName } | Select-Object -First 1

if (-not $dataset) {
    Write-Host "Dataset no existe, creando '$DatasetName'..." -ForegroundColor Yellow
    $createBody = @{
        name = $DatasetName
        defaultMode = "Push"
        tables = @(
            @{
                name = $TableName
                columns = @(
                    @{ name = "tenant_id"; dataType = "string" },
                    @{ name = "period"; dataType = "string" },
                    @{ name = "generated_at"; dataType = "string" },
                    @{ name = "payload_json"; dataType = "string" }
                )
            }
        )
    }

    $dataset = Invoke-PbiApi -Method POST -Path "groups/$workspaceId/datasets?defaultRetentionPolicy=basicFIFO" -Body $createBody
    Write-Host "Dataset creado: $($dataset.name) ($($dataset.id))" -ForegroundColor Green
}
else {
    Write-Host "Dataset ya existe: $($dataset.name) ($($dataset.id))" -ForegroundColor Green
}

Write-Host "\nVariables recomendadas para la API (Container App):" -ForegroundColor Cyan
Write-Host "AIHUB_DASHBOARD_METRICS_SOURCE=powerbi"
Write-Host "AIHUB_POWERBI_WORKSPACE_ID=$workspaceId"
Write-Host "AIHUB_POWERBI_DATASET_ID=$($dataset.id)"
Write-Host "AIHUB_POWERBI_TABLE_NAME=$TableName"

$result = [ordered]@{
    workspace_name = $WorkspaceName
    workspace_id = $workspaceId
    dataset_name = $dataset.name
    dataset_id = $dataset.id
    table_name = $TableName
}

Write-Host "\nResumen:" -ForegroundColor Cyan
$result | ConvertTo-Json -Depth 5
