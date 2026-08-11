param(
    [string]$ResourceGroupName = "rg-ai-opportunity-hub-dev",
    [string]$Location = "eastus",
    [string]$TemplateFile = ".\main.bicep",
    [string]$ParametersFile = ".\main.parameters.json"
)

$ErrorActionPreference = "Stop"

Write-Host "Using subscription:" -ForegroundColor Cyan
az account show --query "{name:name,id:id,tenantId:tenantId}" -o table

Write-Host "Creating or updating resource group $ResourceGroupName in $Location" -ForegroundColor Cyan
az group create --name $ResourceGroupName --location $Location | Out-Null

Write-Host "Deploying AI Opportunity Hub foundation resources" -ForegroundColor Cyan
az deployment group create `
  --resource-group $ResourceGroupName `
  --template-file $TemplateFile `
  --parameters @$ParametersFile `
  --output table
