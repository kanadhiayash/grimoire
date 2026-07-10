# CI and Delivery

CI must run the checks required by the active profile.

## Required

- Deterministic commands
- Least-privilege permissions
- Pinned or trusted actions
- No secret values in logs
- Failure on required-check errors
- Reproducible release steps

Do not make a failing check optional merely to merge a change.
