#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot – CLI entry point.
"""

import argparse
import os
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
║       Binance Futures Testnet Trading Bot            ║
║       Primetrade.ai Assignment — Python Dev Intern   ║
╚══════════════════════════════════════════════════════╝
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit / Stop-Market orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Credentials (prefer env vars)
    creds = parser.add_argument_group("API credentials (or set env vars BINANCE_API_KEY / BINANCE_API_SECRET)")
    creds.add_argument("--api-key", default=None, help="Binance Testnet API key")
    creds.add_argument("--api-secret", default=None, help="Binance Testnet API secret")

    # Order parameters
    order = parser.add_argument_group("Order parameters")
    order.add_argument("--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT")
    order.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    order.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        help="Order type",
    )
    order.add_argument("--qty", required=True, help="Order quantity")
    order.add_argument("--price", default=None, help="Limit / stop price (required for LIMIT and STOP_MARKET)")

    return parser


def resolve_credentials(args) -> tuple[str, str]:
    """Read API key/secret from CLI args or environment variables."""
    api_key = args.api_key or BINANCE_API_KEY
    api_secret = args.api_secret or BINANCE_API_SECRET

    if not api_key or not api_secret:
        print(
            "\n⚠️  API credentials not found.\n"
            "   Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables in your .env file, or\n"
            "   pass --api-key and --api-secret on the command line.\n"
        )
        sys.exit(1)

    return api_key, api_secret


def main():
    load_dotenv()  # Load environment variables from .env if present
    print(BANNER)
    parser = build_parser()
    args = parser.parse_args()

    # 1. Resolve credentials
    api_key, api_secret = resolve_credentials(args)

    # 2. Validate order inputs
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
        validated["symbol"],
        validated["side"],
        validated["order_type"],
        validated["quantity"],
        validated["price"],
    )

    # 3. Build client and place order
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
