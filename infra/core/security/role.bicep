metadata description = 'Creates a role assignment for a service principal.'
param principalId string

@allowed([
  'Device'
  'ForeignGroup'
  'Group'
  'ServicePrincipal'
  'User'
])
param principalType string = 'ServicePrincipal'
param roleDefinitionId string

// Create a deterministic name for the role assignment
var roleAssignmentName = guid(subscription().id, resourceGroup().id, principalId, roleDefinitionId)

// Check if role assignment exists
resource existingRole 'Microsoft.Authorization/roleAssignments@2022-04-01' existing = if (contains(resourceId('Microsoft.Authorization/roleAssignments', roleAssignmentName), 'Microsoft.Authorization/roleAssignments')) {
  name: roleAssignmentName
}

// Only create if it doesn't exist
resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!contains(resourceId('Microsoft.Authorization/roleAssignments', roleAssignmentName), 'Microsoft.Authorization/roleAssignments')) {
  name: roleAssignmentName
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
  }
}
