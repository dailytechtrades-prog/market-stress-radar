## ☕ Support the project

Market Stress Radar is free and open-source.

If you find it useful and want to support ongoing development:
- ☕ Ko-fi: https://ko-fi.com/dailytechtrades
- ❤️ GitHub Sponsors (coming soon)

Donations are optional and do not unlock paid features.

# Market Stress Radar — User Guide

## Quick start (no config required)

```bash
pip install -r requirements.txt
python stress_radar.py
```

This generates:
- Equities stress gauge
- Crypto stress gauge
- Summary JSON and TXT

No email, no setup.

---

## Optional configuration

1. Copy:
```
config.example.py → config.py
```

2. Edit `config.py`.

If `config.py` is missing, the tool safely uses defaults.

---

## Email (optional)

Supported modes:
- none (default)
- smtp_basic (Gmail / Outlook app password)
- gmail_api (stub)
- sendmail (stub)

### SMTP example (Gmail)

```python
EMAIL_MODE = "smtp_basic"
EMAIL_SENDER = "you@gmail.com"
EMAIL_PASSWORD = "APP_PASSWORD"
EMAIL_RECIPIENTS = ["you@gmail.com"]
```

⚠️ Gmail requires an **App Password**, not your normal login password.

If you already use SMTP in another script, you may still need a separate App Password for this tool due to Gmail security policies.
This tool does not bypass Gmail security restrictions and will never request your Google account password.

---

## Output

```
output/
├── equities_gauge.png
├── crypto_gauge.png
├── stress_summary.txt
└── stress_details.json
```

---

## Disclaimer

Educational use only. Not financial advice.
