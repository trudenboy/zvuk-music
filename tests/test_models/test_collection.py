"""Тесты моделей коллекции."""

from zvuk_music.enums import CollectionItemStatus
from zvuk_music.models.collection import Collection, CollectionItem, HiddenCollection


class TestCollectionItem:
    """Тесты CollectionItem."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "ci1",
            "user_id": "100",
            "item_status": "liked",
            "last_modified": "2024-01-01",
            "likes_count": 42,
        }
        item = CollectionItem.de_json(data, mock_client)

        assert item is not None
        assert item.id == "ci1"
        assert item.user_id == "100"
        assert item.item_status == CollectionItemStatus.LIKED
        assert item.likes_count == 42

    def test_de_json_none(self, mock_client):
        assert CollectionItem.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert CollectionItem.de_json({}, mock_client) is None

    def test_is_liked_true(self, mock_client):
        item = CollectionItem.de_json({"id": "1", "item_status": "liked"}, mock_client)
        assert item.is_liked() is True

    def test_is_liked_false(self, mock_client):
        item = CollectionItem.de_json({"id": "1", "item_status": None}, mock_client)
        assert item.is_liked() is False

    def test_de_list(self, mock_client):
        data = [
            {"id": "1", "item_status": "liked"},
            {"id": "2", "item_status": "liked"},
        ]
        items = CollectionItem.de_list(data, mock_client)
        assert len(items) == 2

    def test_unknown_status(self, mock_client):
        """Неизвестный статус не вызывает ошибку."""
        item = CollectionItem.de_json({"id": "1", "item_status": "unknown_status"}, mock_client)
        assert item is not None


class TestCollection:
    """Тесты Collection."""

    def test_de_json_full(self, mock_client, sample_collection_data):
        collection = Collection.de_json(sample_collection_data, mock_client)

        assert collection is not None
        assert len(collection.artists) == 1
        assert len(collection.releases) == 1
        assert len(collection.tracks) == 2
        assert len(collection.episodes) == 0
        assert len(collection.podcasts) == 0
        assert len(collection.playlists) == 0

    def test_de_json_none(self, mock_client):
        assert Collection.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert Collection.de_json({}, mock_client) is None

    def test_default_empty_lists(self, mock_client):
        """Все списковые поля по умолчанию пустые."""
        collection = Collection.de_json({"artists": []}, mock_client)
        assert collection is not None
        assert collection.artists == []
        assert collection.tracks == []
        assert collection.releases == []
        assert collection.podcasts == []
        assert collection.playlists == []
        assert collection.episodes == []
        assert collection.profiles == []
        assert collection.synthesis_playlists == []

    def test_collection_items_are_typed(self, mock_client, sample_collection_data):
        """Элементы коллекции имеют правильный тип."""
        collection = Collection.de_json(sample_collection_data, mock_client)
        assert all(isinstance(item, CollectionItem) for item in collection.tracks)
        assert all(isinstance(item, CollectionItem) for item in collection.artists)


class TestHiddenCollection:
    """Тесты HiddenCollection."""

    def test_de_json_valid(self, mock_client):
        data = {
            "tracks": [
                {"id": "1", "item_status": "liked"},
            ],
            "artists": [
                {"id": "2", "item_status": "liked"},
            ],
        }
        hidden = HiddenCollection.de_json(data, mock_client)

        assert hidden is not None
        assert len(hidden.tracks) == 1
        assert len(hidden.artists) == 1

    def test_de_json_none(self, mock_client):
        assert HiddenCollection.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert HiddenCollection.de_json({}, mock_client) is None

    def test_default_empty_lists(self, mock_client):
        hidden = HiddenCollection.de_json({"tracks": []}, mock_client)
        assert hidden.tracks == []
        assert hidden.artists == []
