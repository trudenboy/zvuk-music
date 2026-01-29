"""Тесты модели Stream."""

import pytest

from zvuk_music import Quality
from zvuk_music.models.stream import Stream, StreamUrls


class TestStream:
    """Тесты Stream."""

    def test_de_json_valid(self, mock_client, sample_stream_data):
        """Тест десериализации валидных данных."""
        stream = Stream.de_json(sample_stream_data, mock_client)

        assert stream is not None
        assert stream.mid == "https://cdn66.zvuk.com/track/5896627/stream?mid=1"
        assert stream.high is None
        assert stream.flacdrm is None
        assert stream.expire_delta == 86400

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        stream = Stream.de_json(None, mock_client)
        assert stream is None

    def test_get_url_mid(self, mock_client, sample_stream_data):
        """Тест получения URL для mid качества."""
        stream = Stream.de_json(sample_stream_data, mock_client)
        url = stream.get_url(Quality.MID)
        assert url == "https://cdn66.zvuk.com/track/5896627/stream?mid=1"

    def test_get_url_high_unavailable_raises(self, mock_client, sample_stream_data):
        """Тест что недоступное high качество вызывает исключение."""
        from zvuk_music.exceptions import SubscriptionRequiredError

        stream = Stream.de_json(sample_stream_data, mock_client)
        with pytest.raises(SubscriptionRequiredError):
            stream.get_url(Quality.HIGH)

    def test_get_url_flac_unavailable_raises(self, mock_client, sample_stream_data):
        """Тест что недоступное FLAC качество вызывает исключение."""
        from zvuk_music.exceptions import SubscriptionRequiredError

        stream = Stream.de_json(sample_stream_data, mock_client)
        with pytest.raises(SubscriptionRequiredError):
            stream.get_url(Quality.FLAC)

    def test_get_url_all_qualities_available(self, mock_client):
        """Тест получения URL когда все качества доступны."""
        data = {
            "expire": "2024-01-16T12:00:00",
            "expire_delta": 86400,
            "mid": "https://example.com/mid",
            "high": "https://example.com/high",
            "flacdrm": "https://example.com/flac",
        }
        stream = Stream.de_json(data, mock_client)

        assert stream.get_url(Quality.MID) == "https://example.com/mid"
        assert stream.get_url(Quality.HIGH) == "https://example.com/high"
        assert stream.get_url(Quality.FLAC) == "https://example.com/flac"

    def test_get_best_available_only_mid(self, mock_client, sample_stream_data):
        """Тест получения лучшего доступного качества (только mid)."""
        stream = Stream.de_json(sample_stream_data, mock_client)
        quality, url = stream.get_best_available()

        assert quality == Quality.MID
        assert url == "https://cdn66.zvuk.com/track/5896627/stream?mid=1"

    def test_get_best_available_with_high(self, mock_client):
        """Тест получения лучшего качества с high."""
        data = {
            "expire": "2024-01-16T12:00:00",
            "expire_delta": 86400,
            "mid": "https://example.com/mid",
            "high": "https://example.com/high",
            "flacdrm": None,
        }
        stream = Stream.de_json(data, mock_client)
        quality, url = stream.get_best_available()

        assert quality == Quality.HIGH
        assert url == "https://example.com/high"

    def test_get_best_available_with_flac(self, mock_client):
        """Тест получения лучшего качества с FLAC."""
        data = {
            "expire": "2024-01-16T12:00:00",
            "expire_delta": 86400,
            "mid": "https://example.com/mid",
            "high": "https://example.com/high",
            "flacdrm": "https://example.com/flac",
        }
        stream = Stream.de_json(data, mock_client)
        quality, url = stream.get_best_available()

        assert quality == Quality.FLAC
        assert url == "https://example.com/flac"


class TestStreamUrls:
    """Тесты StreamUrls."""

    def test_de_json_valid(self, mock_client):
        """Тест десериализации валидных данных."""
        data = {
            "mid": "https://example.com/mid",
            "high": "https://example.com/high",
            "flacdrm": None,
        }
        urls = StreamUrls.de_json(data, mock_client)

        assert urls is not None
        assert urls.mid == "https://example.com/mid"
        assert urls.high == "https://example.com/high"
        assert urls.flacdrm is None

    def test_get_url(self, mock_client):
        """Тест получения URL по качеству."""
        data = {
            "mid": "https://example.com/mid",
            "high": "https://example.com/high",
            "flacdrm": "https://example.com/flac",
        }
        urls = StreamUrls.de_json(data, mock_client)

        assert urls.get_url(Quality.MID) == "https://example.com/mid"
        assert urls.get_url(Quality.HIGH) == "https://example.com/high"
        assert urls.get_url(Quality.FLAC) == "https://example.com/flac"
