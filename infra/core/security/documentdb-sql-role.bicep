metadata name = 'DocumentDB Database Account SQL Role Assignments.'
metadata description = 'Assign RBAC role for data plane access to Azure Cosmos DB for NoSQL.'

@description('Name of the Azure Cosmos DB for NoSQL account.')
param databaseAccountName string

@description('Id of the identity/principal to assign this role in the context of the account.')
param principalId string = ''

@description('Id of the role definition to assign to the targeted principal in the context of the account.')
param roleDefinitionId string

resource databaseAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' existing = {
  name: databaseAccountName
}

// Create a deterministic name for the role assignment
var roleAssignmentName = guid(databaseAccount.id, principalId, roleDefinitionId)

// Check if role assignment exists
resource existingSqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' existing = if (contains(resourceId('Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments', databaseAccountName, roleAssignmentName), 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments')) {
  name: roleAssignmentName
  parent: databaseAccount
}

// Only create if it doesn't exist
resource sqlRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' = if (!contains(resourceId('Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments', databaseAccountName, roleAssignmentName), 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments')) {
  name: roleAssignmentName
  parent: databaseAccount
  properties: {
    principalId: principalId
    roleDefinitionId: roleDefinitionId
    scope: databaseAccount.id
  }
}

output sqlRoleAssignmentId string = sqlRoleAssignment.id
