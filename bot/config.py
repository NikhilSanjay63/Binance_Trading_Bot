import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Credentials
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Base URL for Binance Futures Testnet
BASE_URL = "https://testnet.binancefuture.com"

def is_configured() -> bool:
    """Check if the necessary API credentials are provided."""
    return bool(BINANCE_API_KEY and BINANCE_API_SECRET)
