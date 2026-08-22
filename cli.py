import argparse
import sys

from stock_tracker import (
    create_database,
    fetch_stock_price,
    save_stock_price,
    get_history,
    add_alert,
    display_stock,
    display_history,
    track
)


def main():

    parser = argparse.ArgumentParser(
        description="Stock Price Tracker and Alert System"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    # ========================================================
    # PRICE
    # ========================================================

    price_parser = subparsers.add_parser(
        "price",
        help="Get the latest stock price"
    )

    price_parser.add_argument(
        "symbol",
        help="Stock symbol, for example AAPL"
    )

    # ========================================================
    # TRACK
    # ========================================================

    track_parser = subparsers.add_parser(
        "track",
        help="Start continuous stock tracking"
    )

    # ========================================================
    # HISTORY
    # ========================================================

    history_parser = subparsers.add_parser(
        "history",
        help="Display stored stock history"
    )

    history_parser.add_argument(
        "symbol",
        help="Stock symbol"
    )

    history_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of records to display"
    )

    # ========================================================
    # ALERT
    # ========================================================

    alert_parser = subparsers.add_parser(
        "alert",
        help="Create a stock price alert"
    )

    alert_parser.add_argument(
        "symbol",
        help="Stock symbol"
    )

    alert_parser.add_argument(
        "condition",
        choices=["above", "below"],
        help="Alert condition"
    )

    alert_parser.add_argument(
        "price",
        type=float,
        help="Alert threshold"
    )

    args = parser.parse_args()

    create_database()

    # ========================================================
    # NO COMMAND
    # ========================================================

    if not args.command:

        parser.print_help()
        sys.exit(0)

    # ========================================================
    # PRICE
    # ========================================================

    if args.command == "price":

        stock = fetch_stock_price(
            args.symbol
        )

        if stock:
            display_stock(stock)

        else:
            print(
                f"No stock data found for "
                f"{args.symbol.upper()}."
            )

    # ========================================================
    # TRACK
    # ========================================================

    elif args.command == "track":

        track()

    # ========================================================
    # HISTORY
    # ========================================================

    elif args.command == "history":

        if args.limit <= 0:

            print(
                "Error: limit must be greater than 0."
            )

            sys.exit(1)

        rows = get_history(
            args.symbol,
            args.limit
        )

        display_history(rows)

    # ========================================================
    # ALERT
    # ========================================================

    elif args.command == "alert":

        if args.price <= 0:

            print(
                "Error: price must be greater than 0."
            )

            sys.exit(1)

        add_alert(
            args.symbol,
            args.condition,
            args.price
        )

        print()
        print("Alert created successfully.")
        print(
            f"Symbol    : {args.symbol.upper()}"
        )
        print(
            f"Condition : {args.condition}"
        )
        print(
            f"Threshold : ${args.price:.2f}"
        )


if __name__ == "__main__":
    main()
