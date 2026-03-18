"""Тесты модели GridContentItem."""

from zvuk_music.models.grid import GridContentItem


class TestGridContentItem:
    """Тесты GridContentItem."""

    def test_de_json_valid(self, mock_client):
        """Тест десериализации валидных данных."""
        data = {"id": "12345", "type": "playlist"}
        item = GridContentItem.de_json(data, mock_client)

        assert item is not None
        assert item.id == "12345"
        assert item.type == "playlist"

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        assert GridContentItem.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        """Тест десериализации пустого dict."""
        assert GridContentItem.de_json({}, mock_client) is None

    def test_de_list(self, mock_client):
        """Тест десериализации списка."""
        data = [
            {"id": "100", "type": "playlist"},
            {"id": "200", "type": "artist"},
            {"id": "300", "type": "playlist"},
        ]
        items = GridContentItem.de_list(data, mock_client)

        assert len(items) == 3
        assert items[0].id == "100"
        assert items[0].type == "playlist"
        assert items[1].type == "artist"

    def test_de_list_empty(self, mock_client):
        """Тест десериализации пустого списка."""
        assert GridContentItem.de_list([], mock_client) == []

    def test_de_list_none(self, mock_client):
        """Тест десериализации None списка."""
        assert GridContentItem.de_list(None, mock_client) == []

    def test_id_attrs(self, mock_client):
        """Тест что _id_attrs основаны на id и type."""
        data1 = {"id": "100", "type": "playlist"}
        data2 = {"id": "100", "type": "artist"}
        item1 = GridContentItem.de_json(data1, mock_client)
        item2 = GridContentItem.de_json(data2, mock_client)

        assert item1 != item2
