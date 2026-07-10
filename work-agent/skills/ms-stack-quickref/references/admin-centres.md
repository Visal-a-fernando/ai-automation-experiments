# Admin Centres — Where to Go for What

Bookmark these. Half of L1 work is just knowing which admin centre owns what.

## The main ones

| Centre | URL | What lives here |
|---|---|---|
| Microsoft 365 admin centre | https://admin.microsoft.com | Users, licences, billing, service health, top-level org settings |
| Entra admin centre (formerly AAD) | https://entra.microsoft.com | Identity, groups, conditional access, app registrations, sign-in logs |
| Exchange admin centre | https://admin.exchange.microsoft.com | Mailboxes, transport rules, mail flow, anti-spam |
| Teams admin centre | https://admin.teams.microsoft.com | Teams policies, calling, meeting policies, devices |
| SharePoint admin centre | https://[tenant]-admin.sharepoint.com | Sites, sharing settings, OneDrive admin |
| Intune (Endpoint Manager) | https://intune.microsoft.com | Device enrolment, compliance, app deployment, autopilot |
| Defender | https://security.microsoft.com | Threat alerts, email quarantine, incident response |
| Compliance / Purview | https://compliance.microsoft.com | DLP, retention, eDiscovery, audit log |
| Azure portal | https://portal.azure.com | Subscriptions, resources, IAM at resource level |

## Sneaky ones people forget

- **Microsoft 365 Apps admin centre:** https://config.office.com — for Office app deployment configs (channels, language packs, update rings)
- **Power Platform admin centre:** https://admin.powerplatform.microsoft.com — environments, DLP for Power Automate
- **Old Office 365 message centre stuff:** lives inside admin.microsoft.com under Health > Message centre
- **Service health (when something's broken tenant-wide):** admin.microsoft.com > Health > Service health
- **Audit log search (when you need to prove who did what):** compliance.microsoft.com > Audit (not in M365 admin centre)
- **License assignment via groups:** entra.microsoft.com > Groups > [group] > Licenses

## Useful shortcuts

- **Find a user fast:** admin.microsoft.com > top search bar — fastest way, faster than navigating
- **Reset a user password:** click the user in admin.microsoft.com, "Reset password" on the right pane
- **Block sign-in:** entra.microsoft.com > Users > [user] > Account > Block sign in (also revokes sessions)
- **See all my tenants (if you're an MSP / CSP):** admin.microsoft.com > Partner relationships, or use Lighthouse: https://lighthouse.microsoft.com

## Common "where the hell is X" answers

- **Out-of-office for another user** → Exchange admin centre > Recipients > Mailboxes > [user] > Mailbox features > Automatic replies
- **Convert user mailbox to shared mailbox** → Exchange admin centre > Recipients > Mailboxes > [user] > More > Convert to shared
- **Restore a deleted user (within 30 days)** → admin.microsoft.com > Users > Deleted users
- **Why a user got blocked** → entra.microsoft.com > Sign-in logs, filter by user
- **Quarantined email release** → security.microsoft.com > Review > Quarantine
- **MFA enforcement** → entra.microsoft.com > Conditional Access (not the old "per-user MFA" page — Microsoft is sunsetting that)
