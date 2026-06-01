# Binance Futures Testnet Trading Bot

A lightweight Python CLI application to place **Market**, **Limit**, and **Stop-Market** orders on the [Binance Futures Testnet (USDT-M)](https://demo.binance.com).


---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (auth, signing, HTTP)
│   ├── orders.py          # Order placement logic + formatted output
│   ├── validators.py      # CLI input validation
│   └── logging_config.py  # Structured logging (file + console)
├── logs/
│   └── trading_bot_YYYYMMDD.log   # Auto-created on first run
├── cli.py                 # CLI entry point (argparse)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet Credentials

1. Go to [https://demo.binance.com](https://demo.binance.com)
2. Log in with your GitHub or Google account
3. Navigate to **API Management** → generate an API Key + Secret

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set API Credentials

**Recommended — environment variables:**

```bash
export BINANCE_API_KEY=your_testnet_api_key
export BINANCE_API_SECRET=your_testnet_api_secret
```

**Alternative — CLI flags** (less secure):

```bash
python cli.py --api-key KEY --api-secret SECRET ...
```

---

## How to Run

### Market Order (BUY)

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
```

### Limit Order (SELL)

```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --qty 0.01 --price 3500
```

### Stop-Market Order (bonus)

```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --price 65000
```

### Full help

```bash
python cli.py --help
```

---

## Sample Output

```
╔══════════════════════════════════════════════════════╗
║       Binance Futures Testnet Trading Bot            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝

────────────────────────────────────────────────────────
  📋  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────
────────────────────────────────────────────────────────
  ✅  ORDER RESPONSE
────────────────────────────────────────────────────────
  Order ID   : 4751839201
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Status     : FILLED
  Exec Qty   : 0.001
  Avg Price  : 67412.30
────────────────────────────────────────────────────────

  🎉  Order placed successfully! Order ID: 4751839201
```

---

## Logging

Logs are written to `logs/trading_bot_YYYYMMDD.log`.

- **File**: DEBUG level — every request, response body, and error
- **Console**: INFO level — key events only

Sample log entry:

```
2026-05-17 10:02:11 | INFO     | cli | CLI invoked | symbol=BTCUSDT side=BUY type=MARKET qty=0.001 price=None
2026-05-17 10:02:11 | INFO     | bot.orders | Order success | orderId=4751839201 status=FILLED
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing API credentials | Prints instructions, exits with code 1 |
| Invalid symbol / side / type | Validation error message, exits with code 1 |
| Missing price for LIMIT order | Validation error, exits with code 1 |
| Binance API error (e.g. insufficient margin) | Prints Binance error code + message |
| Network timeout / connection error | Prints network error, logs details |
| Non-JSON response | Handled gracefully with log entry |

---

## Assumptions

- The bot targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`)
- No leverage adjustment is made — the testnet account's default leverage is used
- `timeInForce` defaults to `GTC` (Good Till Cancelled) for LIMIT orders
- Quantity precision is passed as-is; Binance will reject values that violate the symbol's `LOT_SIZE` filter — the error is caught and displayed clearly
- The bot does not persist state between runs — each CLI invocation is a single order

---

## Bonus Features Implemented

- ✅ **Stop-Market order** support (third order type)
- ✅ Coloured/emoji output for clear UX
- ✅ Structured layered architecture (client / orders / validators / CLI)
