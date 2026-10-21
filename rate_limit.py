"""
WorkplacePulse - Per-user rate limiting for Gemini-backed endpoints.

In-memory sliding window keyed by Firebase uid. State is per container instance,
so the effective ceiling is limit x running Cloud Run instances.
Limits are read from the environment on every call; 0 disables a window.
"""

import os
import time
import threading
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from fastapi import Depends, HTTPException, status

from security import verify_firebase_token

DEFAULT_PER_MINUTE = 10
DEFAULT_PER_DAY = 100


def _env_limit(name: str, default: int) -> int:
    try:
        return max(0, int(os.environ.get(name, default)))
    except ValueError:
        return default


class UserRateLimiter:
    def __init__(self) -> None:
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def check(self, uid: str, now: Optional[float] = None) -> Optional[int]:
        """Records a hit for uid. Returns None if allowed, else seconds until retry."""
        per_min = _env_limit("CHAT_RATE_PER_MIN", DEFAULT_PER_MINUTE)
        per_day = _env_limit("CHAT_RATE_PER_DAY", DEFAULT_PER_DAY)
        if not per_min and not per_day:
            return None

        now = time.time() if now is None else now
        with self._lock:
            hits = self._hits[uid]
            while hits and hits[0] <= now - 86400:
                hits.popleft()

            if per_day and len(hits) >= per_day:
                return int(hits[0] + 86400 - now) + 1
            if per_min:
                recent = [t for t in hits if t > now - 60]
                if len(recent) >= per_min:
                    return int(recent[0] + 60 - now) + 1

            hits.append(now)
            return None


limiter = UserRateLimiter()


async def enforce_gemini_rate_limit(user_token: dict = Depends(verify_firebase_token)) -> dict:
    """FastAPI dependency: verifies the Firebase token, then applies the per-uid limit."""
    uid = user_token.get("uid", "anonymous")
    retry_after = limiter.check(uid)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for AI requests. Please wait before trying again.",
            headers={"Retry-After": str(retry_after)},
        )
    return user_token
