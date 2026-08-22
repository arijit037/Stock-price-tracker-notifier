import os
import time
import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict

import requests
from dotenv import load_dotenv

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

DATABASE = "stocks.db"
LOG_FILE = "tracker.log"
API_URL = "https://www.alphavantage.co/query"

# Stocks to monitor
STOCKS = ["AAPL", "TSLA", "GOOGL", "MSFT"]

# Price alerts
ALERTS = {
    "AAPL": {
        "condition": "above",
        "price": 200.00
    },
    "TSLA": {
        "condition": "below",
        "price": 150.00
    },
    "GOOGL": {
        "condition": "above",
        "price": 180.00
    }
}

# Check prices every 60 seconds
CHECK_INTERVAL = 60


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger(__name__)


# ============================================================
# DATABASE
# ============================================================

def create_database():
    """Create required SQLite tables."""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Stock price history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            open_price REAL,
            high_price REAL,
            low_price REAL,
            volume INTEGER,
            timestamp TEXT NOT NULL
        )
    """)

    # Alert configuration
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            condition TEXT NOT NULL,
            threshold REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Alert history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            condition TEXT NOT NULL,
            threshold REAL NOT NULL,
            current_price REAL NOT NULL,
            triggered_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    logger.info("Database ready at '%s'", DATABASE)


# ============================================================
# API
# ============================================================

def fetch_stock_price(symbol: str) -> Optional[Dict]:
    """
    Fetch the latest stock price from Alpha Vantage.
    """

    symbol = symbol.upper().strip()

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        # API rate-limit message
        if "Note" in data:
            logger.warning(
                "API rate limit reached while requesting %s",
                symbol
            )
            print(
                f"[WARNING] API rate limit reached for {symbol}."
            )
            return None

        # API error message
        if "Error Message" in data:
            logger.error(
                "API error for %s: %s",
                symbol,
                data["Error Message"]
            )
            return None

        quote = data.get("Global Quote")

        if not quote:
            logger.warning(
                "No data returned for %s",
                symbol
            )
            return None

        price_text = quote.get("05. price")

        if not price_text:
            logger.warning(
                "Price not available for %s",
                symbol
            )
            return None

        stock = {
            "symbol": symbol,
            "price": float(price_text),
            "open": float(quote.get("02. open", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "volume": int(quote.get("06. volume", 0)),
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        logger.info(
            "%s $%.2f",
            symbol,
            stock["price"]
        )

        return stock

    except requests.exceptions.Timeout:
        logger.error(
            "Request timeout for %s",
            symbol
        )
        print(
            f"[ERROR] Request timed out for {symbol}."
        )
        return None

    except requests.exceptions.ConnectionError:
        logger.error(
            "Connection error for %s",
            symbol
        )
        print(
            f"[ERROR] Internet connection problem for {symbol}."
        )
        return None

    except requests.exceptions.RequestException as error:
        logger.error(
            "Request failed for %s: %s",
            symbol,
            error
        )
        print(
            f"[ERROR] API request failed for {symbol}."
        )
        return None

    except (ValueError, TypeError) as error:
        logger.error(
            "Invalid API data for %s: %s",
            symbol,
            error
        )
        print(
            f"[ERROR] Invalid data received for {symbol}."
        )
        return None


# ============================================================
# DATABASE OPERATIONS
# ============================================================

def save_stock_price(stock: Dict):
    """Save stock price information."""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stock_prices (
            symbol,
            price,
            open_price,
            high_price,
            low_price,
            volume,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        stock["symbol"],
        stock["price"],
        stock["open"],
        stock["high"],
        stock["low"],
        stock["volume"],
        stock["timestamp"]
    ))

    conn.commit()
    conn.close()

    logger.info(
        "Saved %s price to database",
        stock["symbol"]
    )


def add_alert(
    symbol: str,
    condition: str,
    threshold: float
):
    """Add a price alert to the database."""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (
            symbol,
            condition,
            threshold,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        symbol.upper(),
        condition,
        threshold,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()

    logger.info(
        "Alert added: %s %s $%.2f",
        symbol.upper(),
        condition,
        threshold
    )


def get_history(
    symbol: str,
    limit: int = 10
):
    """Get historical stock prices."""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            symbol,
            price,
            open_price,
            high_price,
            low_price,
            volume,
            timestamp
        FROM stock_prices
        WHERE symbol = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        symbol.upper(),
        limit
    ))

    rows = cursor.fetchall()

    conn.close()

    return rows


def save_alert_history(
    symbol: str,
    condition: str,
    threshold: float,
    current_price: float
):
    """Save triggered alert to database."""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alert_history (
            symbol,
            condition,
            threshold,
            current_price,
            triggered_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        symbol,
        condition,
        threshold,
        current_price,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


# ============================================================
# ALERT SYSTEM
# ============================================================

def check_alert(
    symbol: str,
    price: float
):
    """
    Check whether a configured price alert
    has been triggered.
    """

    alert = ALERTS.get(symbol)

    if not alert:
        return

    condition = alert["condition"]
    threshold = alert["price"]

    triggered = False

    if condition == "above" and price > threshold:
        triggered = True

    elif condition == "below" and price < threshold:
        triggered = True

    if not triggered:
        return

    logger.info(
        "ALERT triggered: %s %s $%.2f (price=$%.2f)",
        symbol,
        condition,
        threshold,
        price
    )

    print(
        f"\nALERT: {symbol} is {condition} "
        f"${threshold:.2f} "
        f"(current=${price:.2f})"
    )

    save_alert_history(
        symbol,
        condition,
        threshold,
        price
    )

    send_notification(
        symbol,
        condition,
        threshold,
        price
    )


# ============================================================
# DESKTOP NOTIFICATION
# ============================================================

def send_notification(
    symbol: str,
    condition: str,
    threshold: float,
    price: float
):
    """Send desktop notification."""

    title = "Stock Price Alert"

    message = (
        f"{symbol} is {condition} "
        f"${threshold:.2f}\n"
        f"Current price: ${price:.2f}"
    )

    if not NOTIFICATIONS_AVAILABLE:
        logger.warning(
            "Desktop notifications are unavailable. "
            "Install plyer."
        )
        print(
            "[WARNING] Desktop notifications unavailable."
        )
        return

    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Stock Price Tracker",
            timeout=10
        )

        logger.info(
            "Desktop notification sent for %s",
            symbol
        )

    except Exception as error:
        logger.error(
            "Notification failed for %s: %s",
            symbol,
            error
        )


# ============================================================
# DISPLAY
# ============================================================

def display_stock(stock: Dict):
    """Display stock information in terminal."""

    print()
    print("=" * 60)
    print(f"Stock       : {stock['symbol']}")
    print(f"Price       : ${stock['price']:.2f}")
    print(f"Open        : ${stock['open']:.2f}")
    print(f"High        : ${stock['high']:.2f}")
    print(f"Low         : ${stock['low']:.2f}")
    print(f"Volume      : {stock['volume']:,}")
    print(f"Updated     : {stock['timestamp']}")
    print("=" * 60)


def display_history(rows):
    """Display historical stock prices."""

    if not rows:
        print("No historical data found.")
        return

    print()
    print("=" * 90)
    print(
        f"{'Symbol':<10}"
        f"{'Price':<12}"
        f"{'Open':<12}"
        f"{'High':<12}"
        f"{'Low':<12}"
        f"{'Volume':<15}"
        f"{'Timestamp'}"
    )
    print("-" * 90)

    for row in rows:

        (
            symbol,
            price,
            open_price,
            high,
            low,
            volume,
            timestamp
        ) = row

        print(
            f"{symbol:<10}"
            f"${price:<11.2f}"
            f"${open_price:<11.2f}"
            f"${high:<11.2f}"
            f"${low:<11.2f}"
            f"{volume:<15,}"
            f"{timestamp}"
        )

    print("=" * 90)


# ============================================================
# TRACKING
# ============================================================

def track_once():
    """Fetch and store prices for all configured stocks."""

    print()
    print(
        f"Checking stocks at "
        f"{datetime.now().strftime('%H:%M:%S')}"
    )

    for symbol in STOCKS:

        stock = fetch_stock_price(symbol)

        if stock is None:
            continue

        save_stock_price(stock)

        print(
            f"{symbol:<8} "
            f"${stock['price']:.2f}"
        )

        check_alert(
            symbol,
            stock["price"]
        )


def setup_alerts():
    """Create configured alerts in database."""

    for symbol, alert in ALERTS.items():

        add_alert(
            symbol,
            alert["condition"],
            alert["price"]
        )


# ============================================================
# MAIN TRACKER
# ============================================================

def track():
    """Continuously track configured stocks."""

    if not API_KEY:
        print()
        print("ERROR: API key not found.")
        print()
        print(
            "Create a .env file and add:"
        )
        print()
        print(
            "ALPHA_VANTAGE_API_KEY=YOUR_API_KEY"
        )
        print()
        return

    create_database()

    # Add alerts only if they are not already present
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    for symbol, alert in ALERTS.items():

        cursor.execute("""
            SELECT id
            FROM alerts
            WHERE symbol = ?
            AND condition = ?
            AND threshold = ?
        """, (
            symbol,
            alert["condition"],
            alert["price"]
        ))

        exists = cursor.fetchone()

        if not exists:
            add_alert(
                symbol,
                alert["condition"],
                alert["price"]
            )

    conn.close()

    logger.info(
        "Tracking: %s (interval=%ss)",
        ", ".join(STOCKS),
        CHECK_INTERVAL
    )

    print()
    print("=" * 60)
    print("STOCK PRICE TRACKER")
    print("=" * 60)
    print(
        f"Tracking: {', '.join(STOCKS)}"
    )
    print(
        f"Interval: {CHECK_INTERVAL} seconds"
    )
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    try:

        while True:

            track_once()

            print(
                f"\nNext check in "
                f"{CHECK_INTERVAL} seconds..."
            )

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:

        print()
        print("Tracker stopped by user.")

        logger.info(
            "Stock tracker stopped by user."
        )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":
    track()
