"""Rate limiter for API calls.

Note (RU): Ограничитель частоты запросов к API.
"""

import asyncio
import threading
import time
from typing import Optional


class Throttler:
    """Rate limiter for API calls.

    Limits the number of requests per time period using a token bucket algorithm.
    Thread-safe for sync usage; uses asyncio.Lock for async usage.

    Args:
        rate_limit: Maximum requests per period.
        period: Time period in seconds (default 1.0).

    Warning:
        Do not use the same Throttler instance from both sync (acquire)
        and async (async_acquire) code paths simultaneously. Each path
        uses a different lock type and they do not protect against each other.

    Note (RU): Ограничитель частоты запросов к API.
        Ограничивает количество запросов за период времени
        с использованием алгоритма корзины токенов.
    """

    def __init__(self, rate_limit: int = 5, period: float = 1.0) -> None:
        if rate_limit <= 0:
            raise ValueError(f"rate_limit must be positive, got {rate_limit}")
        if period <= 0:
            raise ValueError(f"period must be positive, got {period}")
        self.rate_limit = rate_limit
        self.period = period
        self._tokens = float(rate_limit)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()
        self._async_lock: Optional[asyncio.Lock] = None

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            float(self.rate_limit),
            self._tokens + elapsed * (self.rate_limit / self.period),
        )
        self._last_refill = now

    def acquire(self) -> None:
        """Block until a request slot is available (sync).

        Note (RU): Блокировать до появления свободного слота (синхронный).
        """
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
            time.sleep(self.period / self.rate_limit)

    async def async_acquire(self) -> None:
        """Wait until a request slot is available (async).

        Note (RU): Ожидать свободный слот (асинхронный).
        """
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()
        while True:
            async with self._async_lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
            await asyncio.sleep(self.period / self.rate_limit)
