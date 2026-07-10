# PowerShell Modules for M365 Admin — Connection Cheat Sheet

Each module needs to be installed once, then connected at the start of each PowerShell session.

## Install all the common ones in one go

```powershell
# Run PowerShell as Administrator OR use -Scope CurrentUser (no admin needed)
Install-Module Microsoft.Graph -Scope CurrentUser -Force
Install-Module ExchangeOnlineManagement -Scope CurrentUser -Force
Install-Module MicrosoftTeams -Scope CurrentUser -Force
Install-Module PnP.PowerShell -Scope CurrentUser -Force
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser -Force
Install-Module AzureAD -Scope CurrentUser -Force   # legacy, still used
Install-Module Az -Scope CurrentUser -Force        # for Azure resources
```

## Connecting

```powershell
# Microsoft Graph (replaces MSOnline and AzureAD for most modern tasks)
Connect-MgGraph -Scopes "User.Read.All","Group.Read.All","Directory.Read.All"

# Exchange Online
Connect-ExchangeOnline -UserPrincipalName admin@tenant.onmicrosoft.com

# Teams
Connect-MicrosoftTeams

# SharePoint Online (admin URL, NOT a site URL)
Connect-SPOService -Url https://tenant-admin.sharepoint.com

# PnP (for site-level work)
Connect-PnPOnline -Url https://tenant.sharepoint.com/sites/SiteName -Interactive

# Azure
Connect-AzAccount
```

## Disconnecting (do this when you finish, especially on shared/client machines)

```powershell
Disconnect-MgGraph
Disconnect-ExchangeOnline -Confirm:$false
Disconnect-MicrosoftTeams
Disconnect-SPOService
Disconnect-PnPOnline
Disconnect-AzAccount
```

## Gotchas

- **MSOnline and AzureAD are deprecated.** Microsoft has been threatening to kill them for years. Learn Graph PowerShell instead — `Get-MgUser`, `Get-MgGroup`, etc.
- **Scopes matter for Graph.** If `Connect-MgGraph` succeeds but commands fail with "Insufficient privileges", you forgot to request the right scope. Reconnect with more scopes.
- **PnP requires app registration for some tenants.** If you hit "The token is not valid", check whether the tenant has disabled legacy auth — you may need `Register-PnPManagementShellAccess`.
- **MFA on admin accounts** breaks any command that uses `-Credential (Get-Credential)`. Always use `-Interactive` or `-UserPrincipalName` flows.

## Common first commands

```powershell
# Who am I connected as
Get-MgContext                     # Graph
Get-ConnectionInformation         # Exchange Online

# List all users
Get-MgUser -All

# List all licensed users
Get-MgUser -All -Property AssignedLicenses | Where-Object { $_.AssignedLicenses.Count -gt 0 }

# Get a mailbox
Get-Mailbox -Identity user@tenant.com | Format-List

# List all SharePoint sites
Get-SPOSite -Limit All

# Get tenant info
Get-MgOrganization
```

## Microsoft Learn refs

- Graph PowerShell: https://learn.microsoft.com/powershell/microsoftgraph/
- Exchange Online: https://learn.microsoft.com/powershell/exchange/exchange-online-powershell
- SharePoint Online: https://learn.microsoft.com/powershell/sharepoint/sharepoint-online/connect-sharepoint-online
- PnP: https://pnp.github.io/powershell/
