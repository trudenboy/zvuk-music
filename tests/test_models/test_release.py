"""Тесты моделей релиза."""

from zvuk_music.enums import ReleaseType
from zvuk_music.models.release import Release, SimpleRelease


class TestSimpleRelease:
    """Тесты SimpleRelease."""

    def test_de_json_valid(self, mock_client):
        """Десериализация валидных данных."""
        data = {
            "id": "669414",
            "title": "Metallica",
            "date": "1991-01-01T00:00:00",
            "type": "album",
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
            "explicit": False,
            "artists": [{"id": "754367", "title": "Metallica", "image": None}],
        }
        release = SimpleRelease.de_json(data, mock_client)

        assert release is not None
        assert release.id == "669414"
        assert release.title == "Metallica"
        assert release.type == ReleaseType.ALBUM
        assert len(release.artists) == 1

    def test_de_json_none(self, mock_client):
        assert SimpleRelease.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert SimpleRelease.de_json({}, mock_client) is None

    def test_de_list(self, mock_client):
        """Десериализация списка."""
        data = [
            {"id": "1", "title": "Release 1"},
            {"id": "2", "title": "Release 2"},
        ]
        releases = SimpleRelease.de_list(data, mock_client)
        assert len(releases) == 2
        assert releases[0].id == "1"

    def test_get_year(self, mock_client):
        """Получение года из даты."""
        release = SimpleRelease.de_json(
            {"id": "1", "title": "Test", "date": "1991-01-01T00:00:00"},
            mock_client,
        )
        assert release.get_year() == 1991

    def test_get_year_none(self, mock_client):
        """get_year возвращает None при отсутствии даты."""
        release = SimpleRelease.de_json(
            {"id": "1", "title": "Test"},
            mock_client,
        )
        assert release.get_year() is None

    def test_default_empty_artists(self, mock_client):
        """По умолчанию artists — пустой список."""
        release = SimpleRelease.de_json({"id": "1", "title": "Test"}, mock_client)
        assert release.artists == []

    def test_unknown_release_type(self, mock_client):
        """Неизвестный тип релиза не вызывает ошибку."""
        data = {"id": "1", "title": "Test", "type": "unknown_type"}
        release = SimpleRelease.de_json(data, mock_client)
        assert release is not None


class TestRelease:
    """Тесты Release."""

    def test_de_json_full(self, mock_client, sample_release_data):
        """Десериализация полных данных."""
        release = Release.de_json(sample_release_data, mock_client)

        assert release is not None
        assert release.id == "669414"
        assert release.title == "Metallica"
        assert release.type == ReleaseType.ALBUM
        assert len(release.genres) == 1
        assert release.genres[0].name == "Rock"
        assert release.label is not None
        assert release.label.title == "EMI"
        assert len(release.artists) == 1

    def test_de_json_none(self, mock_client):
        assert Release.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert Release.de_json({}, mock_client) is None

    def test_get_year(self, mock_client, sample_release_data):
        """Release.get_year работает."""
        release = Release.de_json(sample_release_data, mock_client)
        assert release.get_year() == 1991

    def test_to_dict(self, mock_client, sample_release_data):
        """Сериализация в словарь."""
        release = Release.de_json(sample_release_data, mock_client)
        d = release.to_dict()

        assert isinstance(d, dict)
        assert d["id"] == "669414"
        assert "client" not in d

    def test_default_empty_lists(self, mock_client):
        """По умолчанию списковые поля — пустые."""
        release = Release.de_json({"id": "1", "title": "Test"}, mock_client)
        assert release.genres == []
        assert release.artists == []
        assert release.tracks == []
        assert release.related == []

    def test_get_cover_url(self, mock_client, sample_release_data):
        """get_cover_url возвращает URL."""
        release = Release.de_json(sample_release_data, mock_client)
        url = release.get_cover_url(300)
        assert "zvuk.com" in url

    def test_is_liked_false(self, mock_client, sample_release_data):
        """is_liked без данных."""
        release = Release.de_json(sample_release_data, mock_client)
        assert release.is_liked() is False
