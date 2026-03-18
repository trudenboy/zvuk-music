"""Тесты обработки ошибок HTTP запросов."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from zvuk_music.exceptions import (
    BadRequestError,
    BotDetectedError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimedOutError,
    UnauthorizedError,
    ZvukMusicError,
)
from zvuk_music.utils.request import Request


@pytest.fixture
def request_obj():
    """Создать объект Request без клиента."""
    return Request()


class TestRequestErrors:
    """Тесты обработки ошибок в Request."""

    def test_timeout_raises(self, request_obj):
        """requests.Timeout -> TimedOutError."""
        with (
            patch("requests.request", side_effect=requests.Timeout("timed out")),
            pytest.raises(TimedOutError),
        ):
            request_obj._request_wrapper("GET", "https://example.com")

    def test_401_raises(self, request_obj):
        """HTTP 401 -> UnauthorizedError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.content = b'{"errors": [{"message": "Unauthorized"}]}'
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(UnauthorizedError),
        ):
            request_obj._request_wrapper("GET", "https://example.com")

    def test_403_raises(self, request_obj):
        """HTTP 403 -> UnauthorizedError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.content = b'{"errors": [{"message": "Forbidden"}]}'
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(UnauthorizedError),
        ):
            request_obj._request_wrapper("GET", "https://example.com")

    def test_404_raises(self, request_obj):
        """HTTP 404 -> NotFoundError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.content = b'{"errors": [{"message": "Not found"}]}'
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(NotFoundError),
        ):
            request_obj._request_wrapper("GET", "https://example.com")

    def test_400_raises(self, request_obj):
        """HTTP 400 -> BadRequestError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.content = b'{"errors": [{"message": "Bad request"}]}'
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(BadRequestError),
        ):
            request_obj._request_wrapper("GET", "https://example.com")

    def test_bot_detected_html(self, request_obj):
        """HTML response -> BotDetectedError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"<html><body>Bot activity detected</body></html>"
        with patch("requests.request", return_value=mock_resp):
            result = request_obj._request_wrapper("GET", "https://example.com")
            with pytest.raises(BotDetectedError):
                request_obj._parse(result)

    def test_invalid_json(self, request_obj):
        """Некорректный JSON -> ZvukMusicError."""
        with pytest.raises(ZvukMusicError):
            request_obj._parse(b"not valid json at all {{{")

    def test_429_raises_rate_limit_error(self, request_obj):
        """HTTP 429 -> RateLimitError."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.content = b'{"errors": [{"message": "Too many requests"}]}'
        mock_resp.headers = {}
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(RateLimitError) as exc_info,
        ):
            request_obj._request_wrapper("GET", "https://example.com")
        assert exc_info.value.retry_after is None

    def test_429_with_retry_after_header(self, request_obj):
        """HTTP 429 с Retry-After -> RateLimitError с retry_after."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.content = b'{"errors": [{"message": "Rate limited"}]}'
        mock_resp.headers = {"retry-after": "60"}
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(RateLimitError) as exc_info,
        ):
            request_obj._request_wrapper("GET", "https://example.com")
        assert exc_info.value.retry_after == 60

    def test_429_with_date_retry_after_header(self, request_obj):
        """Non-integer Retry-After -> retry_after=None."""
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.content = b'{"errors": [{"message": "Rate limited"}]}'
        mock_resp.headers = {"retry-after": "Wed, 21 Oct 2025 07:28:00 GMT"}
        with (
            patch("requests.request", return_value=mock_resp),
            pytest.raises(RateLimitError) as exc_info,
        ):
            request_obj._request_wrapper("GET", "https://example.com")
        assert exc_info.value.retry_after is None

    def test_429_is_network_error_subclass(self):
        """RateLimitError наследуется от NetworkError."""
        err = RateLimitError("test", retry_after=30)
        assert isinstance(err, NetworkError)
        assert err.retry_after == 30

    def test_successful_response(self, request_obj):
        """Успешный ответ возвращает данные."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"data": {"tracks": []}}'
        with patch("requests.request", return_value=mock_resp):
            result = request_obj._request_wrapper("GET", "https://example.com")
            assert isinstance(result, bytes)
