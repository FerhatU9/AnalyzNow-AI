<#
.SYNOPSIS
Deploy the AnalyzNow AI fictional-data demo to Azure Container Apps.

This is an explicit, billable cloud operation. Review Azure costs and set
a subscription budget before running it. No credentials are written to Git.
Images must already be publicly pullable from GHCR.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^sha-[0-9a-f]{12}$')]
    [string]$ImageTag,

    [string]$Location = "westeurope",
    [string]$ResourceGroup = "rg-analyznow-demo",
    [string]$EnvironmentName = "env-analyznow-demo",

    [Parameter(Mandatory = $true)]
    [switch]$ApproveCloudCharges
)

$ErrorActionPreference = "Stop"

function Invoke-Azure {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    & az @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Azure command failed: az $($Arguments -join ' ')"
    }
}

if (-not $ApproveCloudCharges) {
    throw "Cloud resources incur charges. Pass -ApproveCloudCharges after checking your Azure subscription and budget."
}

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Install the Azure CLI, sign in with 'az login', and choose your Azure subscription."
}

Invoke-Azure -Arguments @("account", "show", "--query", "{name:name,id:id}", "-o", "table")
Write-Host "Review the Azure subscription above before continuing. Use 'az account set' to change it." -ForegroundColor Yellow
$answer = Read-Host "Type DEPLOY to create Azure resources on this subscription"
if ($answer -cne "DEPLOY") {
    throw "Deployment cancelled; nothing created."
}

$apiName = "analyznow-api-demo"
$webName = "analyznow-web-demo"
$apiImage = "ghcr.io/ferhatu9/analyznow-ai-api:$ImageTag"
$webImage = "ghcr.io/ferhatu9/analyznow-ai-web:$ImageTag"

# Verify both packages have been set public on GitHub, without handling tokens.
foreach ($image in @($apiImage, $webImage)) {
    & docker manifest inspect $image *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot pull $image anonymously. Publish the GitHub container package before running this script."
    }
}

Invoke-Azure -Arguments @("extension", "add", "--name", "containerapp", "--upgrade", "--yes")

# Refuse to modify an existing application; this is a one-time deployment guide.
$existingGroup = & az group exists --name $ResourceGroup
if ($LASTEXITCODE -ne 0) { throw "Unable to inspect resource group $ResourceGroup." }
if ($existingGroup.Trim() -eq "true") {
    $apps = & az containerapp list --resource-group $ResourceGroup --query "[].name" -o tsv
    if ($LASTEXITCODE -ne 0) { throw "Unable to inspect existing Container Apps." }
    if (@($apps) -contains $apiName -or @($apps) -contains $webName) {
        throw "An AnalyzNow container app already exists in this resource group. Stop; do not overwrite an existing deployment."
    }
}

Invoke-Azure -Arguments @("group", "create", "--name", $ResourceGroup, "--location", $Location, "-o", "none")

$envFound = & az containerapp env list --resource-group $ResourceGroup --query "[?name=='$EnvironmentName'].name" -o tsv
if ($LASTEXITCODE -ne 0) { throw "Unable to inspect Container Apps environments." }
if (-not $envFound) {
    Invoke-Azure -Arguments @("containerapp", "env", "create", "--name", $EnvironmentName, "--resource-group", $ResourceGroup, "--location", $Location, "-o", "none")
}

Invoke-Azure -Arguments @(
    "containerapp", "create",
    "--name", $apiName,
    "--resource-group", $ResourceGroup,
    "--environment", $EnvironmentName,
    "--image", $apiImage,
    "--ingress", "internal",
    "--target-port", "9011",
    "--min-replicas", "0",
    "--max-replicas", "1",
    "--cpu", "0.5",
    "--memory", "1Gi",
    "--env-vars",
    "FOOTBALL_DATA_SOURCE=csv",
    "FOOTBALL_CSV_PATH=/app/data/synthetic_demo.csv",
    "ANALYZNOW_PUBLIC_DEMO=1",
    "-o", "none"
)

Invoke-Azure -Arguments @(
    "containerapp", "create",
    "--name", $webName,
    "--resource-group", $ResourceGroup,
    "--environment", $EnvironmentName,
    "--image", $webImage,
    "--ingress", "external",
    "--target-port", "3011",
    "--min-replicas", "0",
    "--max-replicas", "1",
    "--cpu", "0.5",
    "--memory", "1Gi",
    "--env-vars", "FOOTBALL_API_URL=http://$apiName",
    "-o", "none"
)

$hostname = & az containerapp show --name $webName --resource-group $ResourceGroup --query "properties.configuration.ingress.fqdn" -o tsv
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($hostname)) {
    throw "Deployment was created but the public hostname could not be retrieved. Inspect resources in Azure Portal."
}
Write-Host "Website URL: https://$hostname" -ForegroundColor Green
Write-Host "Next: verify /api/teams, synthetic forecast, and browser pages before adding the URL to GitHub."
Write-Host "If you don't need the demo, delete the dedicated resource group in Azure Portal to stop future resource charges."
