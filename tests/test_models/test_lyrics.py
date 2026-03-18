"""Тесты модели Lyrics."""

from zvuk_music.enums import LyricsType
from zvuk_music.models.lyrics import Lyrics


class TestLyrics:
    """Тесты Lyrics."""

    def test_de_json_valid(self, mock_client):
        """Тест десериализации валидных данных."""
        data = {
            "lyrics": "[00:12.00]First line\n[00:15.00]Second line",
            "type": "subtitle",
            "translation": "Первая строка\nВторая строка",
        }
        lyrics = Lyrics.de_json(data, mock_client)

        assert lyrics is not None
        assert lyrics.lyrics == "[00:12.00]First line\n[00:15.00]Second line"
        assert lyrics.type == "subtitle"
        assert lyrics.translation == "Первая строка\nВторая строка"

    def test_de_json_plain_text(self, mock_client):
        """Тест десериализации plain text lyrics."""
        data = {
            "lyrics": "Some plain lyrics text",
            "type": "lyrics",
            "translation": None,
        }
        lyrics = Lyrics.de_json(data, mock_client)

        assert lyrics is not None
        assert lyrics.lyrics == "Some plain lyrics text"
        assert lyrics.type == "lyrics"
        assert lyrics.translation is None

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        assert Lyrics.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        """Тест десериализации пустого dict."""
        assert Lyrics.de_json({}, mock_client) is None

    def test_lyrics_type_subtitle(self, mock_client):
        """lyrics_type возвращает SUBTITLE для synced."""
        lyrics = Lyrics.de_json({"lyrics": "text", "type": "subtitle"}, mock_client)
        assert lyrics.lyrics_type == LyricsType.SUBTITLE

    def test_lyrics_type_plain(self, mock_client):
        """lyrics_type возвращает LYRICS для plain."""
        lyrics = Lyrics.de_json({"lyrics": "text", "type": "lyrics"}, mock_client)
        assert lyrics.lyrics_type == LyricsType.LYRICS

    def test_lyrics_type_unknown(self, mock_client):
        """lyrics_type возвращает None для неизвестного типа."""
        lyrics = Lyrics.de_json({"lyrics": "text", "type": "unknown_type"}, mock_client)
        assert lyrics.lyrics_type is None

    def test_lyrics_type_none(self, mock_client):
        """lyrics_type возвращает None если type не задан."""
        lyrics = Lyrics.de_json({"lyrics": "text"}, mock_client)
        assert lyrics.lyrics_type is None

    def test_is_synced_true(self, mock_client):
        """is_synced возвращает True для subtitle."""
        lyrics = Lyrics.de_json({"lyrics": "text", "type": "subtitle"}, mock_client)
        assert lyrics.is_synced is True

    def test_is_synced_false(self, mock_client):
        """is_synced возвращает False для plain text."""
        lyrics = Lyrics.de_json({"lyrics": "text", "type": "lyrics"}, mock_client)
        assert lyrics.is_synced is False
