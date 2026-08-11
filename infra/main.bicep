targetScope = 'resourceGroup'

@description('Primary Azure region for AI Opportunity Hub resources.')
param location string = resourceGroup().location

@description('Base name used to compose Azure resource names.')
param appName string = 'aiopportunityhub'

@description('Deployment environment suffix such as dev, test or prod.')
param environmentName string = 'dev'

@description('Optional tags to stamp across provisioned resources.')
param tags object = {
  application: 'AI Opportunity Hub'
  environment: environmentName
  managedBy: 'Bicep'
}

@description('Enable PostgreSQL Flexible Server provisioning.')
param enablePostgres bool = false

@description('Enable Azure Container Registry provisioning.')
param enableAcr bool = false

@description('Administrator login for PostgreSQL when enabled.')
param postgresAdminLogin string = 'aihubadmin'

@secure()
@description('Administrator password for PostgreSQL when enabled.')
param postgresAdminPassword string = ''

var effectivePostgresPassword = enablePostgres ? postgresAdminPassword : 'DisabledPostgres123!'

var normalizedApp = toLower(replace(appName, '-', ''))
var shortApp = take(normalizedApp, 14)
var storageName = take('${shortApp}${environmentName}${uniqueString(resourceGroup().id)}', 24)
var acrName = take(replace('${shortApp}${environmentName}acr${uniqueString(resourceGroup().id)}', '-', ''), 50)
var logAnalyticsName = '${appName}-${environmentName}-law'
var appInsightsName = '${appName}-${environmentName}-appi'
var containerAppsEnvName = '${appName}-${environmentName}-cae'
var keyVaultName = take(replace('${appName}-${environmentName}-kv-${uniqueString(resourceGroup().id)}', '-', ''), 24)
var managedIdentityName = '${appName}-${environmentName}-mi'
var postgresServerName = take(replace('${appName}-${environmentName}-psql-${uniqueString(resourceGroup().id)}', '-', ''), 63)
var blobServiceName = 'default'

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: tags
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    accessTier: 'Hot'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: blobServiceName
}

resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'documents'
  properties: {
    publicAccess: 'None'
  }
}

resource artifactsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'artifacts'
  properties: {
    publicAccess: 'None'
  }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = if (enableAcr) {
  name: acrName
  location: location
  sku: {
    name: 'Standard'
  }
  tags: tags
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      retentionPolicy: {
        days: 14
        status: 'enabled'
      }
      trustPolicy: {
        status: 'disabled'
        type: 'Notary'
      }
    }
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: tags
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enabledForDeployment: false
    enabledForTemplateDeployment: false
    enabledForDiskEncryption: false
    publicNetworkAccess: 'Enabled'
    softDeleteRetentionInDays: 90
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        workloadProfileType: 'Consumption'
        name: 'Consumption'
      }
    ]
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = if (enablePostgres) {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  tags: tags
  properties: {
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: effectivePostgresPassword
    authConfig: {
      activeDirectoryAuth: 'Disabled'
      passwordAuth: 'Enabled'
      tenantId: subscription().tenantId
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    createMode: 'Default'
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    storage: {
      storageSizeGB: 32
      autoGrow: 'Enabled'
    }
    version: '16'
  }
}

output containerAppsEnvironmentId string = containerAppsEnvironment.id
output containerAppsEnvironmentName string = containerAppsEnvironment.name
output acrLoginServer string = enableAcr ? registry.properties.loginServer : ''
output acrResourceId string = enableAcr ? registry.id : ''
output storageAccountName string = storage.name
output storageBlobEndpoint string = storage.properties.primaryEndpoints.blob
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output applicationInsightsConnectionString string = appInsights.properties.ConnectionString
output userAssignedIdentityId string = identity.id
output userAssignedIdentityClientId string = identity.properties.clientId
output postgresServerName string = enablePostgres ? postgres.name : ''
output documentsContainerName string = documentsContainer.name
output artifactsContainerName string = artifactsContainer.name