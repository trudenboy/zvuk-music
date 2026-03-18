"""Тесты модели DirectStream."""

from zvuk_music.models.direct_stream import DirectStream


class TestDirectStream:
    """Тесты DirectStream."""

    def test_de_json_valid(self, mock_client):
        """Тест десериализации валидных данных."""
        data = {
            "stream": "https://cdn66.zvuk.com/track/123/stream?direct=1",
            "quality": "high",
        }
        ds = DirectStream.de_json(data, mock_client)

        assert ds is not None
        assert ds.stream == "https://cdn66.zvuk.com/track/123/stream?direct=1"
        assert ds.quality == "high"

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        assert DirectStream.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        """Тест десериализации пустого dict."""
        assert DirectStream.de_json({}, mock_client) is None

    def test_de_json_minimal(self, mock_client):
        """Тест десериализации с минимальными данными."""
        data = {"stream": "https://example.com/stream"}
        ds = DirectStream.de_json(data, mock_client)

        assert ds is not None
        assert ds.stream == "https://example.com/stream"
        assert ds.quality is None

    def test_id_attrs(self, mock_client):
        """Тест что _id_attrs основаны на stream URL."""
        data1 = {"stream": "https://example.com/a", "quality": "high"}
        data2 = {"stream": "https://example.com/a", "quality": "mid"}
        ds1 = DirectStream.de_json(data1, mock_client)
        ds2 = DirectStream.de_json(data2, mock_client)

        assert ds1 == ds2
