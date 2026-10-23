"""Track stock holdings and append valuation snapshots to a CSV file."""

import argparse
import csv
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

CSV_FIELDS = (
    "timestamp",
    "row_type",
    "ticker",
    "shares",
    "buy_price",
    "current_price",
    "invested_value",
    "market_value",
    "gain_loss",
    "gain_loss_pct",
)


def fetch_current_price(ticker):
    """Return Yahoo Finance's latest available regular-market price."""
    symbol = urllib.parse.quote(ticker, safe=".-^=")
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        "?range=1d&interval=1m"
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; PortfolioTracker/1.0)"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.load(response)
        result = payload["chart"]["result"][0]
        price = Decimal(str(result["meta"]["regularMarketPrice"]))
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        KeyError,
        IndexError,
        TypeError,
        InvalidOperation,
    ) as error:
        raise ValueError(f"Could not retrieve a quote for {ticker}: {error}") from error

    if not price.is_finite() or price <= 0:
        raise ValueError(f"The quote for {ticker} was not a positive price.")
    return price


def calculate_holding(ticker, shares, buy_price, current_price):
    """Calculate invested value, market value, and gain or loss for a holding."""
    invested_value = shares * buy_price
    market_value = shares * current_price
    gain_loss = market_value - invested_value
    gain_loss_pct = gain_loss / invested_value * Decimal("100")
    return {
        "row_type": "holding",
        "ticker": ticker,
        "shares": shares,
        "buy_price": buy_price,
        "current_price": current_price,
        "invested_value": invested_value,
        "market_value": market_value,
        "gain_loss": gain_loss,
        "gain_loss_pct": gain_loss_pct,
    }


def build_summary(positions, prices):
    """Return one summary row per ticker followed by a portfolio total row."""
    rows = [
        calculate_holding(
            ticker,
            position["shares"],
            position["buy_price"],
            prices[ticker],
        )
        for ticker, position in positions.items()
    ]
    invested_total = sum((row["invested_value"] for row in rows), Decimal("0"))
    market_total = sum((row["market_value"] for row in rows), Decimal("0"))
    gain_total = market_total - invested_total
    rows.append(
        {
            "row_type": "total",
            "ticker": "PORTFOLIO",
            "shares": "",
            "buy_price": "",
            "current_price": "",
            "invested_value": invested_total,
            "market_value": market_total,
            "gain_loss": gain_total,
            "gain_loss_pct": gain_total / invested_total * Decimal("100"),
        }
    )
    return rows


def write_snapshot(rows, csv_path):
    """Append a timestamped portfolio snapshot, writing the header once."""
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    file_path = Path(csv_path)
    with file_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        if csv_file.tell() == 0:
            writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "timestamp": timestamp,
                    **{
                        field: format(value, "f") if isinstance(value, Decimal) else value
                        for field, value in row.items()
                    },
                }
            )
    return file_path


def prompt_positive_decimal(message):
    while True:
        try:
            value = Decimal(input(message).strip())
            if value.is_finite() and value > 0:
                return value
        except InvalidOperation:
            pass
        print("Enter a number greater than zero.")


def collect_positions():
    """Prompt for one purchase price and share quantity per ticker."""
    positions = {}
    print("Enter holdings. Leave the ticker blank when finished.")
    while True:
        ticker = input("Ticker: ").strip().upper()
        if not ticker:
            break
        if not re.fullmatch(r"[A-Z0-9.^=-]{1,20}", ticker):
            print("Use a valid ticker symbol (letters, numbers, ., -, ^, or =).")
            continue
        if ticker in positions:
            print("That ticker is already listed; enter each ticker once.")
            continue
        buy_price = prompt_positive_decimal(f"{ticker} buy price per share: $")
        shares = prompt_positive_decimal(f"{ticker} number of shares: ")
        positions[ticker] = {"buy_price": buy_price, "shares": shares}
    return positions


def display_summary(rows):
    print()
    print(
        f"{'Ticker':<12}{'Shares':>12}{'Buy price':>14}{'Current':>14}"
        f"{'Invested':>16}{'Market value':>16}{'Gain/Loss':>15}{'Return':>10}"
    )
    print("-" * 109)
    for row in rows:
        print(
            f"{row['ticker']:<12}"
            f"{format_shares(row['shares']):>12}"
            f"{format_money(row['buy_price']):>14}"
            f"{format_money(row['current_price']):>14}"
            f"{format_money(row['invested_value']):>16}"
            f"{format_money(row['market_value']):>16}"
            f"{format_money(row['gain_loss']):>15}"
            f"{format_percent(row['gain_loss_pct']):>10}"
        )


def format_money(value):
    return f"${value:,.2f}" if isinstance(value, Decimal) else "-"


def format_shares(value):
    return f"{value:,.4f}" if isinstance(value, Decimal) else "-"


def format_percent(value):
    return f"{value:+.2f}%" if isinstance(value, Decimal) else "-"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        default="portfolio_summary.csv",
        help="CSV file to append snapshots to (default: portfolio_summary.csv)",
    )
    args = parser.parse_args()

    positions = collect_positions()
    if not positions:
        print("No holdings entered; nothing to value or log.")
        return

    prices = {}
    for ticker in positions:
        print(f"Fetching latest available quote for {ticker}...")
        prices[ticker] = fetch_current_price(ticker)

    rows = build_summary(positions, prices)
    display_summary(rows)
    csv_path = write_snapshot(rows, args.csv)
    print(f"\nSnapshot appended to {csv_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPortfolio tracking cancelled.")
    except (OSError, ValueError) as error:
        raise SystemExit(str(error)) from error