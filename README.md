# AI Value Hub

AI Value Hub is a reference platform that helps organizations capture, validate, and package AI use cases end-to-end — from idea intake to business validation, technical validation, and architecture package generation.

## License
This repository is licensed under MIT.
See the full terms in [LICENSE](LICENSE).

## 📚 Start here
- **[Application Overview](docs/APPLICATION_OVERVIEW.md)** — how the platform works, core flows, and roadmap.
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** — simplest path to run locally or deploy to Azure.
- **[Client Architecture Reference](docs/CLIENT_ARCHITECTURE_REFERENCE.md)** — detailed architecture reference for partners/clients.

> ⚠️ **Note about the diagram files below:** `architecture-diagram.html` and `ai-value-hub-demo.html` are interactive pages, but GitHub's file browser only shows their raw source code when you click them — it does not render HTML. To actually see them rendered, use one of the two options below.

## 🖥️ Viewing the interactive diagrams

### Option A — Live view (once GitHub Pages is enabled)
Requires GitHub Pages to be turned on for this repo (Settings → Pages → Source: `main` / root) and, since the repo is private, requires being signed in to GitHub with read access to it.
- **📊 [Control Center](https://makanto32.github.io/AI-Valu-Hub/)** — main navigation menu
- **💡 [Flow Diagram](https://makanto32.github.io/AI-Valu-Hub/ai-value-hub-demo.html)** — visual walkthrough of the demo
- **🏗️ [Component Architecture (EN)](https://makanto32.github.io/AI-Valu-Hub/architecture-diagram.html)** — full technical diagram
- **🏗️ [Component Architecture (ES)](https://makanto32.github.io/AI-Valu-Hub/architecture-diagram.es.html)** — Spanish version
- **📈 [Fabric + Dashboard Architecture](https://makanto32.github.io/AI-Valu-Hub/architecture-fabric-live.html)** — Microsoft Fabric live integration for executive metrics
- **📖 [Use Case Factory](https://makanto32.github.io/AI-Valu-Hub/AI_Use_Case_Factory_Company_Context_Engine_EN.html)** — executive reference document

### Option B — Open locally (always works, no Pages needed)
```bash
git clone https://github.com/makanto32/AI-Valu-Hub.git
cd AI-Valu-Hub
# Windows
start index.html
# macOS
open index.html
# Linux
xdg-open index.html
```
This opens the same navigation menu and diagrams directly in your default browser, rendered exactly as they would be on Pages.

## Microsoft Fabric integration
- Semantic provider enabled for the executive dashboard via Power BI / Fabric.
- Supporting scripts:
	- `scripts/fabric-provision-semantic.ps1`
	- `scripts/fabric-sync-semantic.ps1`
- Setup reference: `docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md`

## Core capabilities implemented
- Idea intake.
- Per-tenant Context Engine to assess viability against a business baseline.
- Business validation + initial technical filter.
- Use-case status tracking with rejection reasons (business or technical phase).
- UI with demo login flow, context capture, and a dedicated "My ideas" view.
- Per-user isolation: each session only sees its own ideas.
- Multi-language foundation (Spanish as canonical, with English/Portuguese support).

## Technical validation & architecture packaging
- State and artifact persistence in a local DB (SQLite), ready to evolve to PostgreSQL.
- Context file metadata persisted in DB, with content in Blob storage (Azure or local fallback).
- Dedicated endpoint for explicit technical validation.
- Architecture Package generation per idea, including components, integrations, risks, and deployment steps.
- Initial Response Composer that returns an executive summary and next actions.

Key endpoints:
- `POST /ideas/{idea_id}/technical-validate`
- `POST /ideas/{idea_id}/architecture-package`

## Authentication (demo + Entra-ready)
- Default active provider: `AIHUB_AUTH_PROVIDER=demo`.
- Test users:
	- `analista.finanzas / Demo1234!`
	- `analista.riesgo / Demo1234!`
- Endpoints:
	- `POST /auth/login`
	- `GET /auth/me`
	- `GET /ideas/mine`
- Microsoft Entra ID hook already included in code: if `AIHUB_AUTH_PROVIDER=entra`, the API responds `501` until the production integration is completed.

## Roadmap / not yet implemented
See [docs/APPLICATION_OVERVIEW.md](docs/APPLICATION_OVERVIEW.md#roadmap) for the full list, including marketplace-oriented capabilities under evaluation:
- Community voting / upvoting
- Download / adoption metrics
- User comments and reviews
- Publication workflow (draft → published → versioned)
- Admin center with token/cost/ROI governance
- Multi-tenant IaC and packaged deployment per client

## Structure
- `frontend`: React + Vite.
- `api`: FastAPI.
- `workers`: reserved for future capabilities.
- `infra`: Infrastructure as Code (Bicep) for Azure deployment.
- `docs`: architecture references, guides, and scope notes.

## Client-facing reference documentation
- Architecture guide: [docs/CLIENT_ARCHITECTURE_REFERENCE.md](docs/CLIENT_ARCHITECTURE_REFERENCE.md)
- Professional PDF diagram: [docs/AI_Opportunity_Hub_Architecture_Reference.pdf](docs/AI_Opportunity_Hub_Architecture_Reference.pdf)

## Run the API
```bash
pip install -r requirements.txt
uvicorn api.app.main:app --reload --port 8000
```

## Run the Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
API: http://localhost:8000

## Deploy to Azure
See [docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) for the simplest deployment path. Since this repository is private, the standard "Deploy to Azure" portal button cannot be used (it requires a publicly reachable template); instead we provide a one-command deployment script.
