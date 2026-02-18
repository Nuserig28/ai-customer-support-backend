import os
import time
from dotenv import load_dotenv

load_dotenv()

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# { ip: (window_start_ts, count) }
_BUCKET = {}

def check_rate_limit(ip: str):
    now = time.time()
    window = 60.0
    ip = ip or "unknown"

    window_start, count = _BUCKET.get(ip, (now, 0))

    # pencere yenile
    if now - window_start >= window:
        window_start, count = now, 0

    count += 1
    _BUCKET[ip] = (window_start, count)

    if count > RATE_LIMIT_PER_MINUTE:
        raise RuntimeError(f"Rate limit exceeded ({count}/{RATE_LIMIT_PER_MINUTE} per minute) for IP {ip}")
