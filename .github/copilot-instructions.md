# Copilot Deployment Instructions

This file is automatically loaded by GitHub Copilot Agent. It captures known issues,
required workarounds, and the exact deployment steps for this solution accelerator.

---

## Solution Overview

**Agentic Applications for Unified Data Foundation** — deploys a chat interface backed
by an Azure AI Foundry agent that queries structured data via Microsoft Fabric and
policy documents via Azure AI Search. Key Azure resources: AI Foundry, AI Search,
Cosmos DB, Azure SQL, two App Services (API + Web), and Azure Container Registry.

---

## Pre-requisites

Before starting, confirm the following are installed and configured:

| Tool | Minimum Version | Check |
|---|---|---|
| Azure Developer CLI (`azd`) | **>= 1.15.0** (1.28.0+ recommended) | `azd version` |
| Azure CLI (`az`) | >= 2.60.0 | `az version` |
| Python | 3.11.x | `python --version` |
| Node.js | >= 18 | `node --version` |

- Active Azure subscription with Owner or Contributor + User Access Administrator roles
- Microsoft Fabric workspace with **Ontology** and **Graph** features enabled
  (Workspace Settings → Fabric Settings → Fabric Items)

---

## Critical Known Issues — Read Before Deploying

### 1. `IS_WORKSHOP=true` is REQUIRED

Without this flag, `azd provision` will NOT create Azure AI Search or Cosmos DB.
Always set it before provisioning:

```powershell
azd env set IS_WORKSHOP true
```

### 2. `text-embedding-3-small` may be broken in some regions

In regions including **westus3**, the `text-embedding-3-small` model deployment
can show status "Succeeded" in the portal but return HTTP 404 on all data-plane
calls. If this happens:

1. Delete the `text-embedding-3-small` deployment from Azure AI Foundry portal
   (or via CLI: `az cognitiveservices account deployment delete`)
2. Create a new deployment using **`text-embedding-ada-002`** with:
   - SKU: **Standard** (not GlobalStandard)
   - Capacity: **80**
3. Update the environment variable:
   ```powershell
   azd env set AZURE_OPENAI_EMBEDDING_MODEL text-embedding-ada-002
   azd env set AZURE_OPENAI_EMBEDDING_DEPLOYMENT text-embedding-ada-002
   ```

### 3. `acr_build_and_deploy.ps1` — PowerShell pipe issue (now fixed)

The `DOCKER|image:tag` format required by App Service `linuxFxVersion` contains
a `|` character. When PowerShell passes this to `az` (a `.cmd` batch file), cmd.exe
interprets `|` as a pipe operator, breaking the command.

**This is fixed in `infra/scripts/acr_build_and_deploy.ps1`** — it now uses
`az rest` with a JSON body file to set `linuxFxVersion`, bypassing the pipe issue.

If you ever need to set the container image manually outside the script, use:

```powershell
# Write the value to a temp JSON file first (do NOT use --linux-fx-version directly)
$image = "DOCKER|<acr-login-server>/<image>:<tag>"
'{"properties":{"linuxFxVersion":"' + $image + '"}}' | Out-File "$env:TEMP\body.json" -Encoding utf8
$subId = az account show --query id -o tsv
az rest --method patch `
  --uri "https://management.azure.com/subscriptions/$subId/resourceGroups/<rg>/providers/Microsoft.Web/sites/<app-name>/config/web?api-version=2022-03-01" `
  --body "@$env:TEMP\body.json" --output none
```

### 4. Verify subscription before starting

The Azure CLI and azd may have different active subscriptions. Always verify:

```powershell
az account show --query "{name:name, id:id}" -o table
azd env get-values | Select-String AZURE_SUBSCRIPTION
```

If wrong, switch with: `az account set --subscription "<subscription-id>"`

---

## Deployment Steps (in order)

### Step 1 — Verify Azure login and subscription

```powershell
az login
az account show --query "{name:name, id:id}" -o table
# If needed: az account set --subscription "<subscription-id>"
```

### Step 2 — Configure Fabric workspace

In your Microsoft Fabric workspace:
- Go to Workspace Settings → Fabric Settings → Fabric Items
- Enable **Ontology** and **Graph** features
- Note the **Workspace ID** from the URL: `app.fabric.microsoft.com/groups/<workspace-id>`

### Step 3 — Initialize azd environment

```powershell
azd env new <env-name>                              # e.g. rddap5
azd env set IS_WORKSHOP true                        # CRITICAL — do not skip
azd env set FABRIC_WORKSPACE_ID <workspace-id>
```

### Step 4 — Provision and deploy Azure resources

```powershell
azd up
# Answer prompts: subscription, location (recommend eastus or westus3), resource group
```

This creates all Azure resources: AI Foundry, AI Search, Cosmos DB, App Services, ACR, etc.

### Step 5 — Set up Python environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r scripts/requirements.txt
```

### Step 6 — Run the build pipeline

```powershell
python scripts/00_build_solution.py
```

This orchestrates:
- `01_generate_data.py` — generates sample data
- `02_create_fabric_items.py` — creates Fabric lakehouse (~5 min)
- `03_generate_agent_prompt.py` — generates agent system prompt
- `04_upload_to_sql.py` — uploads structured data to SQL
- `05_upload_to_search.py` — indexes documents in AI Search
- `06_create_agent.py` — creates the AI Foundry agent

### Step 7 — Test the agent (optional but recommended)

```powershell
python scripts/07_test_agent.py
```

All 3 test queries should succeed before proceeding to container deployment.

### Step 8 — Configure app settings and RBAC

```powershell
python scripts/08_app_deployment.py
```

### Step 9 — Build containers and deploy to App Services

```powershell
.\infra\scripts\acr_build_and_deploy.ps1
```

This script:
1. Builds the web (React/Nginx) and API (FastAPI) container images remotely in ACR
2. Updates both App Services to use the new images
3. Restarts both App Services

Wait ~2 minutes after the script completes for containers to pull and start.

### Step 10 — Verify deployment

```powershell
$webApp = az webapp show -g <resource-group> -n <web-app-name> --query defaultHostName -o tsv
Start-Process "https://$webApp"
```

The app should show the **"Unified Data Analysis Agents"** chat interface.

---

## Sample Test Questions

Use these in the web app to verify end-to-end functionality:

**SQL / Fabric data questions:**
- "How many tickets are high priority?"
- "What is the average score from inspections?"
- "Show tickets grouped by status."

**Document / AI Search questions:**
- "What constitutes a failed inspection?"
- "How quickly should high priority tickets be resolved?"

**Combined (SQL + Search) questions:**
- "Do any inspections violate quality control standards in our Inspection Procedures?"
- "What is our average inspection score, and does it meet the minimum standard outlined in our Quality Control Standards?"

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| AI Search / Cosmos DB not created | `IS_WORKSHOP` not set | `azd env set IS_WORKSHOP true` then `azd provision` again |
| Embedding calls return 404 | `text-embedding-3-small` broken in region | Switch to `text-embedding-ada-002` (Standard SKU) — see Known Issue #2 |
| App Service shows "Welcome to Azure Container Instances!" placeholder | Container image not set | Run `acr_build_and_deploy.ps1` — now fixed with `az rest` workaround |
| `acr_build_and_deploy.ps1` fails on container update | Was deprecated CLI syntax | Fixed — uses `az rest` + JSON file now |
| `azd up` fails with version error | azd CLI too old | Upgrade: `winget upgrade microsoft.azd` |
| Fabric lakehouse creation times out | Normal — Fabric provisioning is slow | Wait 5–10 min and retry `02_create_fabric_items.py` |
| Agent test queries fail | Agent not created or endpoint wrong | Verify `AZURE_AI_AGENT_ENDPOINT` in `.azure/<env>/.env` |

---

## Environment Variables Reference

Key variables in `.azure/<env-name>/.env` after `azd up`:

| Variable | Description |
|---|---|
| `AZURE_ENV_NAME` | azd environment name |
| `AZURE_RESOURCE_GROUP` | Resource group name |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_AI_ENDPOINT` | AI Foundry endpoint URL |
| `AZURE_AI_AGENT_ENDPOINT` | AI Foundry project endpoint for agents |
| `AZURE_AI_SEARCH_ENDPOINT` | Azure AI Search endpoint |
| `AZURE_OPENAI_EMBEDDING_MODEL` | Embedding model name (use `text-embedding-ada-002` if issues) |
| `FABRIC_WORKSPACE_ID` | Microsoft Fabric workspace GUID |
| `IS_WORKSHOP` | Must be `true` to provision Search + Cosmos DB |
| `AZURE_ENV_CONTAINER_REGISTRY_NAME` | ACR name (without `.azurecr.io`) |
| `API_APP_NAME` | Backend API App Service name |
| `WEB_APP_NAME` | Frontend web App Service name |
