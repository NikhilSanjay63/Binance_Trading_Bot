"""
Order placement logic — sits between the CLI and the BinanceClient.
Formats and prints order summaries; returns structured results.
"""

from typing import Any

from bot.client import BinanceClient, BinanceClientError
from bot.logging_config import get_logger

logger = get_logger(__name__)


def _print_divider(char: str = "─", width: int = 60):
    print(char * width)


def _print_order_request(symbol: str, side: str, order_type: str, quantity: float, price: float | None):
    _print_divider()
    print("  📋  ORDER REQUEST SUMMARY")
    _print_divider()
    print(f"  Symbol     : {symbol}")
    print(f"  Side       : {side}")
    print(f"  Type       : {order_type}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    _print_divider()


def _print_order_response(response: dict):
    _print_divider()
    print("  ✅  ORDER RESPONSE")
    _print_divider()
    print(f"  Order ID   : {response.get('orderId', 'N/A')}")
    print(f"  Client OID : {response.get('clientOrderId', 'N/A')}")
    print(f"  Symbol     : {response.get('symbol', 'N/A')}")
    print(f"  Side       : {response.get('side', 'N/A')}")
    print(f"  Type       : {response.get('type', 'N/A')}")
    print(f"  Status     : {response.get('status', 'N/A')}")
    print(f"  Exec Qty   : {response.get('executedQty', '0')}")
    avg_price = response.get('avgPrice') or response.get('price', 'N/A')
    print(f"  Avg Price  : {avg_price}")
    print(f"  Time       : {response.get('updateTime', 'N/A')}")
    _print_divider()


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
) -> dict[str, Any]:
    """
    Place an order and print a formatted summary.

    Returns a dict with keys:
        success  (bool)
        response (dict | None)
        error    (str | None)
    """
    _print_order_request(symbol, side, order_type, quantity, price)

    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
        _print_order_response(response)
        print(f"\n  🎉  Order placed successfully! Order ID: {response.get('orderId')}\n")
        logger.info(
            "Order success | orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return {"success": True, "response": response, "error": None}

    except BinanceClientError as exc:
        print(f"\n  ❌  Order failed: {exc}\n")
        logger.error("Order failed: %s", exc)
        return {"success": False, "response": None, "error": str(exc)}
