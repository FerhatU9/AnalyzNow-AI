# Live AnalyzNow AI demonstration — Microsoft Azure

This guide describes a **public synthetic-data-only portfolio website**, not a production forecasting or betting system.

The deployment reuses the existing tested Docker images. It does not connect to or migrate the developer's historical PostgreSQL database. No database, paid bookmaker key, external football-data download or real betting odds are needed for the public demonstration.

## Architecture

- **Public Next.js website:** Azure Container App `analyznow-web-demo`, external HTTPS ingress on container port 3011
- **Internal FastAPI backend:** Azure Container App `analyznow-api-demo`, internal-only ingress on container port 9011
- **Dataset:** the existing committed `data/synthetic_demo.csv` with fictional teams and scores, packaged in the API image
- **Container registry:** GitHub Container Registry (GHCR), with separate images for API and web
- **No PostgreSQL instance** in the hosted demo. The existing local Docker + PostgreSQL workflow remains available for development and portfolio explanation.

The public browser communicates only with Next.js. Next.js proxies forecasting requests to the internal FastAPI application through Azure Container Apps' internal app-name network addressing. The public API deployment includes `ANALYZNOW_PUBLIC_DEMO=1`, which disables the live bookmaker endpoint with HTTP 404. An API key is never provided.

## Important cost and safety decisions

Azure Container Apps has a consumption-based billing model and may allow scale-to-zero, but resource groups, logging, storage, image pulls and other related Azure services can still incur charges. **Never assume the entire deployment is free.** Confirm subscription eligibility and current costs in [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/), and create a monthly budget and alerts in Azure Cost Management before running the script.

The script creates a dedicated resource group `rg-analyznow-demo` and one Container Apps environment. It explicitly asks the operator to type `DEPLOY`, and requires `-ApproveCloudCharges`. No Azure or GitHub credential belongs in the repository. Use local `az login` in the CLI rather than copying access tokens into chat.

The images must be publicly readable from GHCR. GitHub may create new container packages as private by default; change the **visibility of both generated packages** to public under your GitHub package settings only after checking the intended source and image content. This releases application images, not private account secrets.

## Step 1 — Publish the tested image pair

1. Merge the approved deployment pull request into `main` only after checks pass.
2. On GitHub, go to **Actions → Publish Demo Container Images → Run workflow**, selecting the `main` branch.
3. Inspect the workflow results and copy the full `sha-XXXXXXXXXXXX` tag from the workflow summary. Both images share this exact source-revision tag.
4. In the repository owner's GitHub **Packages** page, locate `analyznow-ai-api` and `analyznow-ai-web` and configure both packages as **Public**. Do not change the visibility of unrelated packages.
5. From PowerShell with Docker Desktop running, confirm that both tagged images are anonymously readable with `docker manifest inspect` (the deployment script performs the same precheck).

The workflow runs **only when manually requested**. It does not automatically deploy to Azure and does not introduce cloud credentials into GitHub Actions.

## Step 2 — Prepare Azure on your computer

1. Sign into your own Azure subscription using the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows) and `az login`.
2. Select the intended subscription with `az account set --subscription "<subscription ID or name>"` and verify with `az account show -o table`.
3. Set a monthly Azure cost budget and spending alerts in Azure Portal. Budget alerts **notify but do not automatically shut services off**.
4. Review the script at `scripts/deploy_azure_demo.ps1` before running. It creates resources in **West Europe** by default; location and names are configurable.

From the project root:

```powershell
.\scripts\deploy_azure_demo.ps1 -ImageTag "sha-REPLACE_WITH_12_COMMIT_CHARACTERS" -ApproveCloudCharges
```

Use the actual tag reported by GitHub Actions (a 12-character lowercase hexadecimal commit prefix). The script will show your selected subscription and require the exact word `DEPLOY` before provisioning.

Azure must be able to pull both images anonymously. The script creates two Container Apps with their own CPU and memory limits, with **0–1 replicas** each, and then displays the public HTTPS website URL. If you have already deployed an app with the same name in the dedicated resource group, the script refuses to overwrite it. Do not rerun destructive cleanup commands to resolve errors.

## Step 3 — Test the deployed site before publishing the link

Visit the HTTPS URL shown by the script. Allow the app to wake from idle and then verify:

1. `/api/teams` returns `dataset_label: "Synthetic demonstration data"`, fictional `Demo City` / `Demo East` teams and last recorded match date `2025-07-18`.
2. The homepage loads; select two different fictional teams and click **Generate Forecast**. Confirm expected goals, outcome probabilities, data freshness and a synthetic-data notice.
3. `/data-health` and `/model-quality` are accessible.
4. The **public** URL does not expose a backend HTTP port or credentials. The backend has **internal-only** ingress. Confirm the private API setting in Azure Portal.
5. Check Azure Container App logs if anything fails; do not claim the site is live until the end-to-end test succeeds.

Only **after successful live verification**, set the repository **About → Website** field to the actual HTTPS URL and add the same URL near the top of the README. Never guess or invent a deployment URL.

## Operations and limitations

- Both services may scale to zero, so a cold start is expected. This is a portfolio demonstration rather than an availability-guaranteed service.
- Public traffic still consumes resources; request limits, authentication, alerting, full hardening and budget controls need additional work before real-world use.
- GitHub Container Registry images must remain public or an authenticated Azure image-pull identity must be configured.
- Deployments are **manual**. No Azure GitHub secrets are required, and publishing an image does not itself update running Azure apps.
- Public users see only synthetic statistics. It is not a live 2026/27 football forecasting service, a production analytical product or a betting platform.
- The resource group can be deleted from Azure Portal when no longer needed to stop most charges associated with the demo; review the full subscription's billable resources before deletion.

## Cleanup

In Azure Portal, inspect `rg-analyznow-demo` carefully and confirm that it contains **only resources created for this demonstration** before using **Delete resource group**. This is destructive and permanently removes its resources. Do not delete the original local Docker volumes or the historical results database.
