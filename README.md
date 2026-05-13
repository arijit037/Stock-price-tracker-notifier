# 📈 Stock Price Tracker & Notifier

Real-time stock monitoring with desktop + email alerts — built with Python.

---

## 🗂️ Project Structure

```
stock_tracker/
├── stock_tracker.py   ← Core engine (prices, alerts, DB, notifications)
├── cli.py             ← Interactive command-line interface
├── requirements.txt   ← Python dependencies
├── .env               ← Your private email credentials (never commit this!)
├── stocks.db          ← SQLite database (auto-created on first run)
└── tracker.log        ← Log file (auto-created on first run)
```

---

## 🛠️ Step-by-Step Setup

### Step 1 — Install Python 3.11+

Download from https://python.org/downloads  
During install: ✅ tick **"Add Python to PATH"**

Verify:
```bash
python --version
# Python 3.11.x  ✅
```

---

### Step 2 — Create Project Folder

```bash
mkdir stock_tracker
cd stock_tracker
```

Copy all 4 files (stock_tracker.py, cli.py, requirements.txt, .env) into this folder.

---

### Step 3 — Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when it's active.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

Packages installed:
| Package | Purpose |
|---------|---------|
| `yfinance` | Fetches real stock prices from Yahoo Finance |
| `plyer` | Sends desktop (OS) notifications |
| `python-dotenv` | Loads email credentials from .env file |
| `requests` | HTTP library (used by yfinance) |

---

### Step 5 — Configure Email Alerts (Optional)

Edit the `.env` file:

```env
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx   ← Gmail App Password (see below)
EMAIL_RECIPIENT=you@example.com
```

#### How to get a Gmail App Password:
1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification**
3. Go to **App Passwords** → Select app: Mail → Select device: Other
4. Copy the 16-character password into EMAIL_PASSWORD in `.env`

> 💡 Leave `.env` blank to skip emails — desktop pop-ups still work.

---

### Step 6 — Edit Your Stocks & Alerts

Open `stock_tracker.py` and scroll to the bottom (`__main__` block):

```python
# Add alerts
add_alert(conn, "AAPL",  "above", 200.00)   # alert when Apple > $200
add_alert(conn, "TSLA",  "below", 150.00)   # alert when Tesla < $150

# Set which stocks to watch and how often (seconds)
track(
    symbols  = ["AAPL", "TSLA", "GOOGL", "MSFT"],
    interval = 60,    # check every 60 seconds
    conn     = conn,
)
```

Common ticker symbols:
- `AAPL` – Apple
- `TSLA` – Tesla
- `GOOGL` – Google
- `MSFT` – Microsoft
- `AMZN` – Amazon
- `NFLX` – Netflix
- `RELIANCE.NS` – Reliance Industries (Indian stocks use `.NS` suffix)
- `TCS.NS` – Tata Consultancy Services

---

### Step 7 — Run the Tracker

```bash
# Option A: Direct tracker (runs forever until Ctrl+C)
python stock_tracker.py

# Option B: Interactive CLI (manage alerts, check prices, view history)
python cli.py
```

#### Sample output:
```
─────────────────────────────────────────────  14:32:01
AAPL    $197.45
TSLA    $148.30   🚨 ALERT triggered: TSLA below $150.00
GOOGL   $172.10
MSFT    $415.88
```

---

## 🔔 How Alerts Work

1. You define a rule: e.g., `TSLA below $150`
2. The tracker checks prices every 60 seconds
3. When Tesla drops below $150:
   - A **desktop pop-up** appears instantly
   - An **email** is sent to your inbox
   - The alert is **deactivated** (so you don't get spammed)
4. Add a new alert whenever you want to monitor again

---

## 💡 Tips & Customization

| Goal | What to change |
|------|---------------|
| Check every 5 minutes | `interval = 300` |
| Add more stocks | Add symbols to the `symbols` list |
| Keep alerts repeating | Remove `deactivate_alert()` call |
| Run overnight | Use Windows Task Scheduler or cron |

### Run automatically on startup (Windows):
1. Press `Win + R` → type `shell:startup`
2. Create a `.bat` file there:
```batch
@echo off
cd C:\path\to\stock_tracker
call venv\Scripts\activate
python stock_tracker.py
```

### Run automatically on startup (macOS/Linux):
Add to crontab (`crontab -e`):
```
@reboot cd /path/to/stock_tracker && source venv/bin/activate && python stock_tracker.py
```

---

## ⚠️ Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with venv active |
| `No data returned` | Check ticker symbol (Indian stocks need `.NS`) |
| Email not sending | Verify App Password in `.env`; check Gmail security settings |
| Desktop notifications not showing | Ensure `plyer` is installed; on Linux install `libnotify` |

---

## 📄 License
Free to use and modify for personal or educational purposes.
# Stock-price-tracker-notifier
