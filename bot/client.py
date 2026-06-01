"""
Binance Futures Testnet client.
Handles HMAC-SHA256 request signing and raw REST calls via `requests`.
"""

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import get_logger

BASE_URL = "https://demo-fapi.binance.com"

logger = get_logger(__name__)


class BinanceClientError(Exception):
    """Raised for Binance API-level errors (non-2xx or error body)."""


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> dict:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = True,
    ) -> Any:
        params = params or {}
        if signed:
            params["timestamp"] = self._timestamp()
            params = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        logger.debug(
            "REQUEST  %s %s | params=%s",
            method.upper(),
            url,
            {k: v for k, v in params.items() if k != "signature"},
        )

        try:
            # FIX: POST must send params in request body, not URL query string
            if method.upper() == "POST":
                resp = self.session.request(method, url, data=params, timeout=10)
            else:
                resp = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error reaching Binance: %s", exc)
            raise BinanceClientError(f"Network error: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out: %s %s", method, url)
            raise BinanceClientError("Request timed out.")

        logger.debug(
            "RESPONSE %s %s | status=%d | body=%s",
            method.upper(),
            url,
            resp.status_code,
            resp.text[:500],
        )

        try:
            data = resp.json()
        except ValueError:
            logger.error("Non-JSON response: %s", resp.text[:200])
            raise BinanceClientError(
                f"Non-JSON response (HTTP {resp.status_code}): {resp.text[:200]}"
            )

        # FIX: Binance error codes are negative integers (e.g. -1102).
        # Success responses have no top-level "code" field at all.
        if not resp.ok or (
            isinstance(data, dict)
            and isinstance(data.get("code"), int)
            and data["code"] < 0
        ):
            msg = data.get("msg", str(data)) if isinstance(data, dict) else str(data)
            code = data.get("code", resp.status_code) if isinstance(data, dict) else resp.status_code
            logger.error("Binance API error | code=%s | msg=%s", code, msg)
            raise BinanceClientError(f"Binance error {code}: {msg}")

        return data

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

    def get_account(self) -> dict:
        return self._request("GET", "/fapi/v2/account")

    def new_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        time_in_force: str = "GTC",
        stop_price: float | None = None,
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET" and stop_price is not None:
            params["stopPrice"] = stop_price

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s stop_price=%s",
            side, order_type, symbol, quantity, price, stop_price,
        )
        return self._request("POST", "/fapi/v1/order", params=params)

    def get_order(self, symbol: str, order_id: int) -> dict:
        return self._request("GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        return self._request("DELETE", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})