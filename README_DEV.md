# Market Stress Radar — Developer Notes

## Design goals

- Zero-config default run
- No external services required
- Email fully optional
- Public-repo safe

## Config loading

`config.py` is optional and imported dynamically.

If missing:
- Defaults are used
- No error is raised

## Email architecture

- smtp_basic: implemented
- gmail_api: stub
- sendmail: stub

This avoids forcing OAuth or system dependencies on users.

## Extension ideas

- Add overall gauge
- Add scheduler helpers
- Add macro calendar API (optional)

PRs welcome.
