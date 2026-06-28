# Implementation Guide

## Enterprise SSO (SAML) onboarding
SSO is available on the Enterprise tier and supports SAML 2.0 identity
providers including Okta, Azure AD, and Google Workspace.

### Steps
1. Confirm the customer's IdP (e.g., Okta).
2. Exchange SAML metadata and configure the connection.
3. Map user attributes and provision roles.
4. Run a pilot with admin accounts, then roll out org-wide.

Typical SSO implementation takes 1-2 weeks. SSO requests are a common renewal
blocker for security-conscious enterprises and should be prioritised.
