"""Тесты обработки ошибок HTTP запросов."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from zvuk_music.exceptions import (
    BadRequestError,
    BotDetectedError,
    NotFoundError,
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

    def test_successful_response(self, request_obj):
        """Успешный ответ возвращает данные."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"data": {"tracks": []}}'
        with patch("requests.request", return_value=mock_resp):
            result = request_obj._request_wrapper("GET", "https://example.com")
            assert isinstance(result, bytes)
