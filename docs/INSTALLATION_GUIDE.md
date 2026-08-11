# Installation Guide

This guide covers the supported ways to run AI Value Hub: a **local run** (fastest way to try it) and an **Azure deployment** (for a shared, cloud-hosted environment).

## Fastest path — Deploy to Azure in one click

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmakanto32%2FAI-Valu-Hub%2Fmain%2Finfra%2Fmain.json)

This opens the Azure Portal with the ARM template (`infra/main.json`) pre-loaded. Pick a subscription and resource group, review the parameters, and click Create. No local tooling required.

---

## Option 1 — Run locally (simplest)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Steps
```bash
# 1. Clone the repository
git clone https://github.com/makanto32/AI-Valu-Hub.git
cd AI-Value-Hub

# 2. Start the API
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload --port 8000

# 3. In a second terminal, start the frontend
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Demo login users: `analista.finanzas / Demo1234!`, `analista.riesgo / Demo1234!`

No Azure account or cloud resources are required for this option. Data is persisted locally in SQLite (`data/aihub.db`) and local file storage.

---

## Option 2 — Deploy to Azure (one command)

This provisions the foundation resources (Container Apps environment, Storage, Key Vault, Log Analytics, Application Insights, optional PostgreSQL/ACR) used to host the API and frontend in Azure.

### Prerequisites
- An Azure subscription
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed and logged in (`az login`)
- Contributor access on the target subscription or resource group

### Steps
```powershell
# 1. Clone the repository
git clone https://github.com/makanto32/AI-Valu-Hub.git
cd AI-Value-Hub/infra

# 2. Log in to Azure (if not already)
az login

# 3. Run the one-command deployment script
./deploy-foundation.ps1 -ResourceGroupName "rg-ai-value-hub-dev" -Location "eastus"
```

This single script:
1. Creates (or reuses) the target resource group.
2. Deploys `main.bicep` with the parameters in `main.parameters.json`.
3. Prints the provisioned resource names when complete.

### What gets deployed
| Resource | Purpose |
|---|---|
| Azure Container Apps Environment | Hosts the API and frontend containers |
| Azure Storage Account | Blob storage for context documents and generated artifacts |
| Azure Key Vault | Secret storage with RBAC |
| Log Analytics Workspace | Centralized logging |
| Application Insights | Telemetry |
| User Assigned Managed Identity | Identity for Container Apps to access other resources |
| PostgreSQL Flexible Server *(optional)* | Enable via `-enablePostgres` for production-grade persistence |
| Azure Container Registry *(optional)* | Enable via `-enableAcr` if you need a private image registry |

### Publishing the application containers
Once the foundation is deployed, publish the API and frontend images to Container Apps:
```powershell
./update-container-apps.ps1 `
  -ResourceGroupName "rg-ai-value-hub-dev" `
  -ApiContainerAppName "aivaluehub-dev-api" `
  -ApiImage "<acr-login-server>/aihub/api:latest" `
  -FrontendContainerAppName "aivaluehub-dev-frontend" `
  -FrontendImage "<acr-login-server>/aihub/frontend:latest"
```

### Configuration notes
- `enablePostgres` and `enableAcr` default to `false` to keep the first deployment simple and secret-free.
- Environment variables and secrets (e.g., Azure Storage connection, Entra ID settings) should be configured through Key Vault references once the Container Apps are created — avoid hardcoding secrets in app settings.
- See `infra/README.md` for full parameter reference.

---

## Troubleshooting
- **`az` not recognized**: install the Azure CLI and restart your terminal.
- **Deployment fails on naming conflicts**: resource names are derived from `appName` + `environmentName` + a uniqueString hash; change `appName` in `main.parameters.json` if you need a different namespace.
- **Container App shows unhealthy**: confirm the ingress `targetPort` is `8000` (the port the FastAPI/uvicorn process listens on).
