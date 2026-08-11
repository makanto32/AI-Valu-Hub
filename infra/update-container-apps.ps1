param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $false)]
    [string]$ApiContainerAppName = "",

    [Parameter(Mandatory = $false)]
    [string]$FrontendContainerAppName = "",

    [Parameter(Mandatory = $false)]
    [string]$ApiImage = "",

    [Parameter(Mandatory = $false)]
    [string]$FrontendImage = "",

    [Parameter(Mandatory = $false)]
    [string]$RevisionSuffix = ""
)

$ErrorActionPreference = "Stop"

if (-not $ApiImage -and -not $FrontendImage) {
    throw "Debes indicar al menos una imagen: -ApiImage y/o -FrontendImage"
}

if ($ApiImage -and -not $ApiContainerAppName) {
    throw "Si defines -ApiImage debes definir -ApiContainerAppName"
}

if ($FrontendImage -and -not $FrontendContainerAppName) {
    throw "Si defines -FrontendImage debes definir -FrontendContainerAppName"
}

if (-not $RevisionSuffix) {
    $RevisionSuffix = (Get-Date -Format "yyyyMMddHHmm")
}

function Assert-AzCli {
    $azCmd = Get-Command az -ErrorAction SilentlyContinue
    if (-not $azCmd) {
        throw "Azure CLI no esta instalado o no esta en PATH."
    }

    $null = az account show --query id -o tsv 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "No hay sesion activa en Azure CLI. Ejecuta: az login"
    }
}

function Update-ContainerAppImage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Image
    )

    Write-Host "Actualizando Container App '$Name' con imagen '$Image'..." -ForegroundColor Cyan

    $exists = az containerapp show --resource-group $ResourceGroupName --name $Name --query name -o tsv 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $exists) {
        throw "No existe la Container App '$Name' en el resource group '$ResourceGroupName'."
    }

    az containerapp update `
        --resource-group $ResourceGroupName `
        --name $Name `
        --image $Image `
        --revision-suffix $RevisionSuffix `
        --output table

    if ($LASTEXITCODE -ne 0) {
        throw "Fallo la actualizacion de '$Name'."
    }

    $fqdn = az containerapp show --resource-group $ResourceGroupName --name $Name --query properties.configuration.ingress.fqdn -o tsv
    $activeRevision = az containerapp show --resource-group $ResourceGroupName --name $Name --query properties.latestRevisionName -o tsv

    Write-Host "Container App actualizada: $Name" -ForegroundColor Green
    Write-Host "Revision activa: $activeRevision" -ForegroundColor Green
    if ($fqdn) {
        Write-Host "Endpoint: https://$fqdn" -ForegroundColor Green
    }
}

Assert-AzCli

if ($ApiImage) {
    Update-ContainerAppImage -Name $ApiContainerAppName -Image $ApiImage
}

if ($FrontendImage) {
    Update-ContainerAppImage -Name $FrontendContainerAppName -Image $FrontendImage
}

Write-Host "Actualizacion completada." -ForegroundColor Green
