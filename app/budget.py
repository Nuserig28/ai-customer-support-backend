import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

DAILY_TOKEN_BUDGET = int(os.getenv("DAILY_TOKEN_BUDGET", "30000"))

# RAM'de günlük sayım: {"date": "YYYY-MM-DD", "tokens": int}
_STATE = {"date": str(date.today()), "tokens": 0}

def check_and_add(tokens_to_add: int):
    if tokens_to_add < 0:
        raise RuntimeError("Invalid token usage")

    today = str(date.today())
    if _STATE["date"] != today:
        _STATE["date"] = today
        _STATE["tokens"] = 0

    if _STATE["tokens"] + tokens_to_add > DAILY_TOKEN_BUDGET:
        raise RuntimeError(
            f"Daily token budget exceeded ({_STATE['tokens']} + {tokens_to_add} > {DAILY_TOKEN_BUDGET})"
        )

    _STATE["tokens"] += tokens_to_add
    return _STATE["tokens"], DAILY_TOKEN_BUDGET
