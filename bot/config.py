import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "dNqcWxofgFUq0aAYl65JYgvbdrrGMg1O0uel9Nbhyuml7rvmSduOWbFaRySpLOCN")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "EDpbIjS7cLczOclwrpcWo6aoJVaK1VOBdGE6syNVSZmqGnij2LdKa4zePNNbmUJz")
BASE_URL = "https://testnet.binancefuture.com"


def is_configured() -> bool:
    return bool(BINANCE_API_KEY and BINANCE_API_SECRET)