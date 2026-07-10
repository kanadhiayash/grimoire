# Observability

Maintained systems should expose enough information to diagnose failures without exposing sensitive data.

## Required where applicable

- Structured logs
- Stable error categories
- Request or operation correlation
- Health checks
- Actionable failure messages
- Redaction of secrets and personal data

Do not log credentials, full tokens, sensitive payloads, or unnecessary personal information.
