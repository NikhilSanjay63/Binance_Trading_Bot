"""Input validation helpers for trading bot CLI."""

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol or len(symbol) < 3:
        raise ValidationError(f"Invalid symbol: '{symbol}'. Example: BTCUSDT")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side: '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type: '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity: '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be > 0, got: {qty}")
    return qty


def validate_price(price: str | None, order_type: str) -> float | None:
    """Price is required for LIMIT and STOP_MARKET orders."""
    if order_type in {"LIMIT", "STOP_MARKET"}:
        if price is None:
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid price: '{price}'. Must be a positive number.")
        if p <= 0:
            raise ValidationError(f"Price must be > 0, got: {p}")
        return p
    return None  # MARKET orders don't need a price


def validate_all(symbol: str, side: str, order_type: str, quantity: str, price: str | None):
    """Run all validators and return cleaned values as a dict."""
    sym = validate_symbol(symbol)
    sd = validate_side(side)
    ot = validate_order_type(order_type)
    qty = validate_quantity(quantity)
    pr = validate_price(price, ot)
    return {"symbol": sym, "side": sd, "order_type": ot, "quantity": qty, "price": pr}
