"""Authenticated Kalshi API wrapper.

RSA-PSS signed requests as specified in the spec:
  - Sign timestamp_ms + METHOD + path
  - path includes /trade-api/v2 prefix, EXCLUDES query string
  - RSA-PSS / SHA-256 / MGF1-SHA-256 / salt = digest length (32 bytes)
  - Base64-encoded signature
  - Headers: KALSHI-ACCESS-KEY, KALSHI-ACCESS-SIGNATURE, KALSHI-ACCESS-TIMESTAMP
  - Timestamp is Unix milliseconds (not seconds)

Environment:
  KALSHI_ENV=demo|prod
  KALSHI_API_KEY_ID
  KALSHI_PRIVATE_KEY_PATH   (path to the .pem file Kalshi gave you)
"""
from __future__ import annotations

import base64
import os
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

HOSTS = {
    "demo": "https://demo-api.kalshi.co",
    "prod": "https://api.elections.kalshi.com",
}
PREFIX = "/trade-api/v2"


class KalshiClient:
    def __init__(self, env: str | None = None,
                 api_key_id: str | None = None,
                 private_key_path: str | None = None):
        env = env or os.getenv("KALSHI_ENV", "demo")
        if env not in HOSTS:
            raise ValueError(f"KALSHI_ENV must be 'demo' or 'prod', got {env!r}")
        self.env = env
        self.host = HOSTS[env]
        self.api_key_id = api_key_id or os.environ["KALSHI_API_KEY_ID"]

        key_path = private_key_path or os.environ["KALSHI_PRIVATE_KEY_PATH"]
        with Path(key_path).open("rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
        self.s = requests.Session()

    # ---- signing -----------------------------------------------------

    def _sign(self, method: str, path: str) -> tuple[str, str]:
        ts_ms = str(int(time.time() * 1000))
        msg = (ts_ms + method.upper() + path).encode("utf-8")
        sig = self.private_key.sign(
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        return ts_ms, base64.b64encode(sig).decode("ascii")

    def _headers(self, method: str, path: str) -> dict:
        ts, sig = self._sign(method, path)
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": sig,
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "accept": "application/json",
            "content-type": "application/json",
        }

    # ---- low-level ---------------------------------------------------

    def request(self, method: str, path: str,
                params: dict | None = None,
                body: dict | None = None) -> dict:
        if not path.startswith(PREFIX):
            path = PREFIX + path
        url = self.host + path
        sign_path = urlparse(url).path
        last_err: Exception | None = None
        for attempt in range(5):
            # re-sign each retry so timestamps stay fresh (signing window)
            headers = self._headers(method, sign_path)
            try:
                r = self.s.request(method, url, params=params, json=body,
                                   headers=headers, timeout=20)
            except requests.RequestException as e:
                last_err = e
                time.sleep(min(8, 0.5 * (2 ** attempt)))
                continue
            if r.status_code == 429:
                # rate-limited: exponential with jitter
                import random
                time.sleep(min(8, (1 + attempt) * 1.5 + random.random()))
                continue
            if r.status_code == 401:
                # auth fail: don't retry, fail loudly
                raise RuntimeError(f"AUTH FAIL {method} {path}: {r.text[:200]}")
            if r.status_code >= 500:
                time.sleep(min(8, 1 + attempt * 2))
                continue
            try:
                data = r.json()
            except ValueError:
                data = {"raw": r.text}
            if r.status_code >= 400:
                # 4xx (client) errors aren't worth retrying; raise immediately
                raise RuntimeError(f"{method} {path} -> {r.status_code}: {data}")
            return data
        raise RuntimeError(f"giving up after retries: {method} {path} "
                           f"(last_err={last_err})")

    # ---- high-level market data --------------------------------------

    def get_event(self, event_ticker: str) -> dict:
        return self.request("GET", f"/events/{event_ticker}")

    def list_markets(self, event_ticker: str) -> list[dict]:
        d = self.request("GET", "/markets",
                         params={"event_ticker": event_ticker, "limit": 50})
        return d.get("markets", [])

    def get_market(self, ticker: str) -> dict:
        return self.request("GET", f"/markets/{ticker}").get("market", {})

    def get_orderbook(self, ticker: str) -> dict:
        return self.request("GET", f"/markets/{ticker}/orderbook")

    # ---- portfolio / orders ------------------------------------------

    def get_balance(self) -> dict:
        return self.request("GET", "/portfolio/balance")

    def get_positions(self) -> list[dict]:
        d = self.request("GET", "/portfolio/positions",
                         params={"limit": 200})
        return d.get("market_positions", []) + d.get("event_positions", [])

    def get_orders(self, status: str | None = None) -> list[dict]:
        params = {"limit": 200}
        if status:
            params["status"] = status
        d = self.request("GET", "/portfolio/orders", params=params)
        return d.get("orders", [])

    def place_order(self, ticker: str, side: str, action: str,
                    count: int, type_: str = "limit",
                    yes_price_cents: int | None = None,
                    no_price_cents: int | None = None,
                    client_order_id: str | None = None,
                    expiration_ts: int | None = None) -> dict:
        """Place an order. side='yes'|'no'. action='buy'|'sell'.
        Use client_order_id for idempotency (default: uuid4).
        """
        body = {
            "ticker": ticker,
            "side": side,
            "action": action,
            "count": int(count),
            "type": type_,
            "client_order_id": client_order_id or str(uuid.uuid4()),
        }
        if yes_price_cents is not None:
            body["yes_price"] = int(yes_price_cents)
        if no_price_cents is not None:
            body["no_price"] = int(no_price_cents)
        if expiration_ts is not None:
            body["expiration_ts"] = int(expiration_ts)
        return self.request("POST", "/portfolio/orders", body=body)

    def cancel_order(self, order_id: str) -> dict:
        return self.request("DELETE", f"/portfolio/orders/{order_id}")
