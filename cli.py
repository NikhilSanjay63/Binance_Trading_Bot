#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot — CLI entry point.

Usage examples
--------------
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.01 --price 3500
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --price 60000
"""

import argparse
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient
from bot.config import BINANCE_API_KEY, BINANCE_API_SECRET
from bot.logging_config import get_logger
from bot.orders import place_order
from bot.validators import ValidationError, validate_all

logger = get_logger("cli")

BANNER = """
╔══════════════════════════════════════════════════════╗
║        Binance Futures Testnet Trading Bot           ║
╚══════════════════════════════════════════════════════╝
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit / Stop-Market orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    creds = parser.add_argument_group("API credentials (or set BINANCE_API_KEY / BINANCE_API_SECRET in env / .env)")
    creds.add_argument("--api-key", default=None, help="Binance Testnet API key")
    creds.add_argument("--api-secret", default=None, help="Binance Testnet API secret")

    order = parser.add_argument_group("Order parameters")
    order.add_argument("--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT")
    order.add_argument("--side", required=True, choices=["BUY", "SELL"])
    order.add_argument("--type", dest="order_type", required=True, choices=["MARKET", "LIMIT", "STOP_MARKET"])
    order.add_argument("--qty", required=True, help="Order quantity")
    order.add_argument("--price", default=None, help="Limit price (LIMIT) or stop trigger price (STOP_MARKET)")

    return parser


def resolve_credentials(args) -> tuple[str, str]:
    api_key = args.api_key or BINANCE_API_KEY
    api_secret = args.api_secret or BINANCE_API_SECRET

    if not api_key or not api_secret:
        print(
            "\n⚠️  API credentials not found.\n"
            "   Options:\n"
            "     1. Create a .env file with BINANCE_API_KEY and BINANCE_API_SECRET\n"
            "     2. Export them as environment variables\n"
            "     3. Pass --api-key and --api-secret on the command line\n"
        )
        sys.exit(1)

    return api_key, api_secret


def main():
    load_dotenv()
    print(BANNER)

    parser = build_parser()
    args = parser.parse_args()

    api_key, api_secret = resolve_credentials(args)

    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.qty,
            price=args.price,
        )
    except ValidationError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(1)

    logger.info(
        "CLI invoked | symbol=%s side=%s type=%s qty=%s price=%s",
        validated["symbol"], validated["side"], validated["order_type"],
        validated["quantity"], validated["price"],
    )

    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    result = place_order(
        client=client,
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["order_type"],
        quantity=validated["quantity"],
        price=validated["price"],
    )

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()