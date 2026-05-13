"""
cli.py  –  Interactive command-line interface for the Stock Tracker
Run:  python cli.py
"""

import sys
from stock_tracker import init_db, add_alert, get_active_alerts, get_price

conn = init_db()


def menu():
    print("""
╔══════════════════════════════════╗
║   📈  Stock Tracker CLI          ║
╠══════════════════════════════════╣
║  1. View active alerts           ║
║  2. Add a new alert              ║
║  3. Check price right now        ║
║  4. View price history           ║
║  5. Exit                         ║
╚══════════════════════════════════╝
""")


def view_alerts():
    alerts = get_active_alerts(conn)
    if not alerts:
        print("  No active alerts.")
        return
    print(f"\n  {'ID':<5} {'Symbol':<8} {'Type':<8} {'Threshold':>10}")
    print("  " + "─" * 35)
    for a in alerts:
        print(f"  {a['id']:<5} {a['symbol']:<8} {a['alert_type']:<8} ${a['threshold']:>9.2f}")


def add_alert_interactive():
    symbol    = input("  Ticker symbol (e.g. AAPL): ").strip().upper()
    kind      = input("  Alert type – above / below: ").strip().lower()
    threshold = float(input("  Price threshold (e.g. 200.00): $").strip())
    if kind not in ("above", "below"):
        print("  Invalid type. Use 'above' or 'below'.")
        return
    add_alert(conn, symbol, kind, threshold)
    print(f"  ✅ Alert saved: {symbol} {kind} ${threshold:.2f}")


def check_price_now():
    symbol = input("  Ticker symbol: ").strip().upper()
    price  = get_price(symbol)
    if price:
        print(f"  {symbol}: ${price:.2f}")


def view_history():
    symbol = input("  Ticker symbol: ").strip().upper()
    cur = conn.execute(
        "SELECT price, recorded_at FROM price_history "
        "WHERE symbol = ? ORDER BY recorded_at DESC LIMIT 20",
        (symbol,),
    )
    rows = cur.fetchall()
    if not rows:
        print("  No history found.")
        return
    print(f"\n  {'Price':>10}   {'Time'}")
    print("  " + "─" * 35)
    for price, ts in rows:
        print(f"  ${price:>9.2f}   {ts}")


def main():
    while True:
        menu()
        choice = input("  Choose [1-5]: ").strip()
        if choice == "1":
            view_alerts()
        elif choice == "2":
            add_alert_interactive()
        elif choice == "3":
            check_price_now()
        elif choice == "4":
            view_history()
        elif choice == "5":
            print("  Goodbye! 👋")
            sys.exit(0)
        else:
            print("  Invalid choice.")
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
