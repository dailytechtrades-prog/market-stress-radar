# ==========================================
# Market Stress Radar — User Configuration
# ==========================================
# Copy this file to config.py to customize.
# ==========================================

# ===== Markets =====
ENABLE_EQUITIES = True
ENABLE_CRYPTO   = True

# ===== Overall weighting =====
EQUITIES_WEIGHT = 0.6
CRYPTO_WEIGHT   = 0.4

# ===== Output =====
OUTPUT_DIR   = "output"
RENDER_GAUGE = True
SAVE_OUTPUT  = True
VERBOSE      = True

# ==========================================
# EMAIL (OPTIONAL)
# ==========================================
# Modes:
# "none"        -> disabled (default)
# "smtp_basic"  -> Gmail / Outlook app password
# "gmail_api"   -> OAuth (stub)
# "sendmail"    -> Linux sendmail (stub)

EMAIL_MODE = "none"

# --- smtp_basic ---
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = ""   # App password recommended
EMAIL_RECIPIENTS = [
    # "you@example.com",
]

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_SUBJECT_PREFIX = "Market Stress Radar"

# ===== Data =====
LOOKBACK_DAYS = 180
