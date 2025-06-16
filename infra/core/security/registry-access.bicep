metadata description = 'Assigns ACR Pull permissions to access an Azure Container Registry.'
param containerRegistryName string
param principalId string

var acrPullRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')

// Create a deterministic name for the role assignment
var roleAssignmentName = guid(subscription().id, resourceGroup().id, principalId, acrPullRole)

// Check if role assignment exists
resource existingAksAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' existing = if (contains(resourceId('Microsoft.Authorization/roleAssignments', roleAssignmentName), 'Microsoft.Authorization/roleAssignments')) {
  name: roleAssignmentName
  scope: containerRegistry
}

// Only create if it doesn't exist
resource aksAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!contains(resourceId('Microsoft.Authorization/roleAssignments', roleAssignmentName), 'Microsoft.Authorization/roleAssignments')) {
  scope: containerRegistry // Use when specifying a scope that is different than the deployment scope
  name: roleAssignmentName
  properties: {
    roleDefinitionId: acrPullRole
    principalType: 'ServicePrincipal'
    principalId: principalId
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' existing = {
  name: containerRegistryName
}
