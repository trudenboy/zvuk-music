"""Тесты Throttler."""

import time

import pytest

from zvuk_music.utils.throttler import Throttler


class TestThrottlerValidation:
    """Тесты валидации параметров."""

    def test_rate_limit_zero_raises(self):
        """rate_limit=0 вызывает ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            Throttler(rate_limit=0)

    def test_rate_limit_negative_raises(self):
        """rate_limit=-1 вызывает ValueError."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            Throttler(rate_limit=-1)

    def test_period_zero_raises(self):
        """period=0 вызывает ValueError."""
        with pytest.raises(ValueError, match="period must be positive"):
            Throttler(rate_limit=5, period=0)

    def test_period_negative_raises(self):
        """period=-1.0 вызывает ValueError."""
        with pytest.raises(ValueError, match="period must be positive"):
            Throttler(rate_limit=5, period=-1.0)


class TestThrottler:
    """Тесты Throttler."""

    def test_initial_tokens_available(self):
        """Начальные токены доступны сразу."""
        throttler = Throttler(rate_limit=5, period=1.0)
        start = time.monotonic()
        for _ in range(5):
            throttler.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 2.0

    def test_blocks_after_exhaustion(self):
        """Блокирует после исчерпания токенов."""
        throttler = Throttler(rate_limit=2, period=1.0)
        throttler.acquire()
        throttler.acquire()
        start = time.monotonic()
        throttler.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.3

    def test_refill_over_time(self):
        """Токены пополняются со временем."""
        throttler = Throttler(rate_limit=10, period=1.0)
        for _ in range(10):
            throttler.acquire()
        time.sleep(0.5)
        start = time.monotonic()
        throttler.acquire()
        elapsed = time.monotonic() - start
        assert elapsed < 2.0

    def test_rate_limit_one(self):
        """Работает с rate_limit=1."""
        throttler = Throttler(rate_limit=1, period=1.0)
        throttler.acquire()
        start = time.monotonic()
        throttler.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.5

    def test_custom_period(self):
        """Работает с пользовательским периодом."""
        throttler = Throttler(rate_limit=2, period=0.5)
        throttler.acquire()
        throttler.acquire()
        start = time.monotonic()
        throttler.acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.15


@pytest.mark.asyncio
class TestThrottlerAsync:
    """Тесты асинхронного Throttler."""

    async def test_async_acquire(self):
        """async_acquire работает."""
        throttler = Throttler(rate_limit=5, period=1.0)
        for _ in range(5):
            await throttler.async_acquire()

    async def test_async_blocks_after_exhaustion(self):
        """Асинхронный блокирует после исчерпания."""
        throttler = Throttler(rate_limit=2, period=1.0)
        await throttler.async_acquire()
        await throttler.async_acquire()
        start = time.monotonic()
        await throttler.async_acquire()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.3
