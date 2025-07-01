# Function to safely get environment variable
function Get-EnvValue {
    param (
        [string]$varName
    )
    $value = $(azd env get-value $varName)
    return $value
}

# Function to delete a resource if it exists
function Remove-AzureResource {
    param (
        [string]$resourceName,
        [string]$resourceGroup,
        [string]$resourceType,
        [string]$displayName
    )
    if (![string]::IsNullOrEmpty($resourceName) -and ![string]::IsNullOrEmpty($resourceGroup)) {
        Write-Host ("Deleting {0}: {1} from resource group: {2}" -f $displayName, $resourceName, $resourceGroup)
        az resource delete --name $resourceName --resource-group $resourceGroup --resource-type $resourceType --verbose
    }
}

# Get all resource information
$resources = @(
    @{
        name = $(Get-EnvValue "AZURE_OPENAI_SERVICE")
        group = $(Get-EnvValue "AZURE_OPENAI_RESOURCE_GROUP")
        type = "Microsoft.CognitiveServices/accounts"
        display = "Azure OpenAI Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_SEARCH_SERVICE")
        group = $(Get-EnvValue "AZURE_SEARCH_SERVICE_RESOURCE_GROUP")
        type = "Microsoft.Search/searchServices"
        display = "Azure Cognitive Search Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_STORAGE_ACCOUNT")
        group = $(Get-EnvValue "AZURE_STORAGE_RESOURCE_GROUP")
        type = "Microsoft.Storage/storageAccounts"
        display = "Storage Account"
    },
    @{
        name = $(Get-EnvValue "AZURE_APP_SERVICE")
        group = $(Get-EnvValue "AZURE_RESOURCE_GROUP")
        type = "Microsoft.Web/sites"
        display = "App Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_APP_SERVICE_PLAN")
        group = $(Get-EnvValue "AZURE_RESOURCE_GROUP")
        type = "Microsoft.Web/serverfarms"
        display = "App Service Plan"
    },
    @{
        name = $(Get-EnvValue "AZURE_DOCUMENTINTELLIGENCE_SERVICE")
        group = $(Get-EnvValue "AZURE_DOCUMENTINTELLIGENCE_RESOURCE_GROUP")
        type = "Microsoft.CognitiveServices/accounts"
        display = "Document Intelligence Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_COMPUTER_VISION_SERVICE")
        group = $(Get-EnvValue "AZURE_COMPUTER_VISION_RESOURCE_GROUP")
        type = "Microsoft.CognitiveServices/accounts"
        display = "Computer Vision Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_SPEECH_SERVICE")
        group = $(Get-EnvValue "AZURE_SPEECH_SERVICE_RESOURCE_GROUP")
        type = "Microsoft.CognitiveServices/accounts"
        display = "Speech Service"
    },
    @{
        name = $(Get-EnvValue "AZURE_APPLICATION_INSIGHTS")
        group = $(Get-EnvValue "AZURE_RESOURCE_GROUP")
        type = "Microsoft.Insights/components"
        display = "Application Insights"
    },
    @{
        name = $(Get-EnvValue "AZURE_LOG_ANALYTICS")
        group = $(Get-EnvValue "AZURE_RESOURCE_GROUP")
        type = "Microsoft.OperationalInsights/workspaces"
        display = "Log Analytics Workspace"
    }
)

# Display resources that will be deleted
Write-Host "`nThe following resources will be deleted:`n"
foreach ($resource in $resources) {
    if (![string]::IsNullOrEmpty($resource.name)) {
        Write-Host ("${0}: {1} in resource group: {2}" -f $resource.display, $resource.name, $resource.group)
    }
}

# Get confirmation
$confirmation = Read-Host "`nAre you sure you want to delete these resources? (y/n)"
if ($confirmation -ne 'y') {
    Write-Host "Operation cancelled"
    exit 0
}

# Delete resources
Write-Host "`nDeleting resources..."
foreach ($resource in $resources) {
    if (![string]::IsNullOrEmpty($resource.name)) {
        Remove-AzureResource -resourceName $resource.name -resourceGroup $resource.group -resourceType $resource.type -displayName $resource.display
    }
}

Write-Host "`nResource deletion process completed."
Write-Host "Note: Some resources like Cognitive Services may remain in soft-delete state for 48 hours."
Write-Host "If you need to immediately reuse the same names, you'll need to purge them from the soft-delete state in the Azure portal." 