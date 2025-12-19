#!/usr/bin/env python3
"""
Market Stress Radar (v1.2)

- Robust optional config.py import
- EMAIL_MODE correctly respected
- Safe defaults if no config.py exists
- smtp_basic implemented
- gmail_api / sendmail remain stubs
"""

from datetime import datetime, date
import calendar, math, json, smtplib, ssl
from pathlib import Path
from email.message import EmailMessage
from email.utils import make_msgid

import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle

# ======================================================
# DEFAULTS (SAFE FOR PUBLIC USE)
# ======================================================
ENABLE_EQUITIES = True
ENABLE_CRYPTO = True

EQUITIES_WEIGHT = 0.6
CRYPTO_WEIGHT = 0.4

OUTPUT_DIR = "output"

EMAIL_MODE = "none"   # none | smtp_basic | gmail_api | sendmail
EMAIL_SUBJECT_PREFIX = "Market Stress Radar"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_RECIPIENTS = []

LOOKBACK_DAYS = 180

# ======================================================
# OPTIONAL USER CONFIG
# ======================================================
try:
    from config import *   # noqa: F401,F403
except Exception:
    pass

# ======================================================
# HELPERS
# ======================================================
def clamp(x):
    return max(0, min(100, x))

def status(score):
    if score <= 25: return "CALM"
    if score <= 45: return "ELEVATED"
    if score <= 65: return "STRESSED"
    return "CRISIS"

# ======================================================
# MACRO DETECTION
# ======================================================
def macro_stress():
    today = date.today()
    events = []

    events.append((date(today.year, today.month, 14), "CPI"))

    for wk in calendar.monthcalendar(today.year, today.month):
        if wk[calendar.FRIDAY]:
            events.append((date(today.year, today.month, wk[calendar.FRIDAY]), "NFP"))
            break

    if today.month in [1,3,5,6,7,9,11,12]:
        events.append((date(today.year, today.month, 15), "FOMC"))

    future = [(d,n) for d,n in events if d >= today]
    if not future:
        return 15, "No immediate macro risk."

    d,n = min(future)
    days = (d - today).days

    if days <= 0: return 90, f"{n} today."
    if days <= 1: return 80, f"{n} imminent."
    if days <= 3: return 65, f"{n} approaching."
    if days <= 7: return 40, f"{n} this week."
    return 20, "No major macro risk soon."

# ======================================================
# DATA
# ======================================================
def series(ticker):
    df = yf.download(
        ticker,
        period=f"{LOOKBACK_DAYS}d",
        progress=False,
        auto_adjust=True
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" in df.columns:
        s = df["Close"]
    else:
        raise RuntimeError(f"No usable price column for {ticker}")

    return s.dropna()

# ======================================================
# STRESS CALCS
# ======================================================
def equities_stress():
    vix = series("^VIX").iloc[-1]
    spx = series("^GSPC")
    tnx = series("^TNX").iloc[-1]
    dxy = series("DX-Y.NYB").iloc[-1]

    vix_s = clamp((vix - 12) * 4)
    trend_s = 60 if spx.iloc[-1] < spx.rolling(50).mean().iloc[-1] else 25
    yield_s = clamp((tnx - 40) * 2)
    usd_s = clamp((dxy - 100) * 1.5)
    macro_s, note = macro_stress()

    score = (
        0.30*vix_s +
        0.20*trend_s +
        0.20*yield_s +
        0.15*usd_s +
        0.15*macro_s
    )
    return clamp(score), note

def crypto_stress():
    btc = series("BTC-USD")
    vol = btc.pct_change().rolling(14).std().iloc[-1] * 100
    trend = 60 if btc.iloc[-1] < btc.rolling(50).mean().iloc[-1] else 30
    return clamp(vol*1.2 + trend)

# ======================================================
# GAUGE
# ======================================================
def render_gauge(score, label, title, filename):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.axis("off")

    bands = [
        (0,25,"#2ecc71"),
        (25,45,"#f1c40f"),
        (45,65,"#e67e22"),
        (65,100,"#e74c3c"),
    ]

    for lo,hi,c in bands:
        ax.add_patch(Wedge((0,0),1,180-hi*1.8,180-lo*1.8,width=0.25,color=c))

    ang = math.radians(180-score*1.8)
    ax.plot([0,math.cos(ang)],[0,math.sin(ang)],lw=4)
    ax.add_patch(Circle((0,0),0.03))

    ax.text(0,0.55,title,ha="center",fontsize=12,weight="bold")
    ax.text(0,0.3,f"{int(score)} — {label}",ha="center",fontsize=16,weight="bold")

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    plt.savefig(Path(OUTPUT_DIR)/filename,bbox_inches="tight")
    plt.close()

# ======================================================
# EMAIL
# ======================================================
def send_email_smtp(subject, html, images):
    if not EMAIL_RECIPIENTS:
        return

    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECIPIENTS)
    msg["Subject"] = subject
    msg.set_content("Market Stress Radar update")
    msg.add_alternative(html, subtype="html")

    for cid, path in images.items():
        with open(path,"rb") as f:
            msg.get_payload()[1].add_related(
                f.read(),
                maintype="image",
                subtype="png",
                cid=cid
            )

    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=ctx)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def send_email(overall, label):
    if EMAIL_MODE == "none":
        return

    cid_eq = make_msgid()
    cid_cr = make_msgid()

    html = f"""
    <html><body>
    <h2>Overall Market Stress: {int(overall)} — {label}</h2>
    <h3>Equities</h3><img src="cid:{cid_eq[1:-1]}"><br>
    <h3>Crypto</h3><img src="cid:{cid_cr[1:-1]}">
    <p style="font-size:12px;color:#666;">Context only, not financial advice.</p>
    </body></html>
    """

    images = {
        cid_eq: Path(OUTPUT_DIR)/"equities_gauge.png",
        cid_cr: Path(OUTPUT_DIR)/"crypto_gauge.png",
    }

    if EMAIL_MODE == "smtp_basic":
        send_email_smtp(f"{EMAIL_SUBJECT_PREFIX} — {label} ({int(overall)})", html, images)
    elif EMAIL_MODE == "gmail_api":
        print("gmail_api mode is a stub (not implemented).")
    elif EMAIL_MODE == "sendmail":
        print("sendmail mode is a stub (not implemented).")

# ======================================================
# MAIN
# ======================================================
def main():
    eq, cr = 0, 0
    notes = []

    if ENABLE_EQUITIES:
        eq, note = equities_stress()
        notes.append(note)

    if ENABLE_CRYPTO:
        cr = crypto_stress()

    overall = clamp(eq*EQUITIES_WEIGHT + cr*CRYPTO_WEIGHT)
    label = status(overall)

    render_gauge(eq, status(eq), "Equities Stress", "equities_gauge.png")
    render_gauge(cr, status(cr), "Crypto Stress", "crypto_gauge.png")

    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    Path(OUTPUT_DIR,"stress_summary.txt").write_text(
        json.dumps({
            "overall":int(overall),
            "status":label,
            "equities":int(eq),
            "crypto":int(cr),
            "notes":notes,
            "generated":datetime.now().isoformat()
        }, indent=2)
    )

    print(f"Overall Market Stress: {int(overall)} — {label}")
    send_email(overall, label)

if __name__ == "__main__":
    main()
