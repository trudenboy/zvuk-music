"""Тесты модели Track."""

import pytest

from zvuk_music.models.track import SimpleTrack, Track


class TestSimpleTrack:
    """Тесты SimpleTrack."""

    def test_de_json_valid(self, mock_client):
        """Тест десериализации валидных данных."""
        data = {
            "id": "5896627",
            "title": "Nothing Else Matters",
            "duration": 388,
            "explicit": False,
            "artists": [{"id": "754367", "title": "Metallica", "image": None}],
            "release": None,
        }
        track = SimpleTrack.de_json(data, mock_client)

        assert track is not None
        assert track.id == "5896627"
        assert track.title == "Nothing Else Matters"
        assert track.duration == 388
        assert track.explicit is False
        assert len(track.artists) == 1
        assert track.artists[0].title == "Metallica"

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        track = SimpleTrack.de_json(None, mock_client)
        assert track is None

    def test_de_json_empty_dict(self, mock_client):
        """Тест десериализации пустого словаря возвращает None."""
        track = SimpleTrack.de_json({}, mock_client)
        # Пустой словарь не является валидными данными для трека
        assert track is None

    def test_de_list(self, mock_client):
        """Тест десериализации списка."""
        data = [
            {"id": "1", "title": "Track 1", "duration": 100, "explicit": False},
            {"id": "2", "title": "Track 2", "duration": 200, "explicit": True},
        ]
        tracks = SimpleTrack.de_list(data, mock_client)

        assert len(tracks) == 2
        assert tracks[0].id == "1"
        assert tracks[1].id == "2"

    def test_get_duration_str(self, mock_client):
        """Тест форматирования длительности."""
        track = SimpleTrack.de_json(
            {"id": "1", "title": "Test", "duration": 185, "explicit": False},
            mock_client,
        )
        assert track.get_duration_str() == "3:05"

    def test_get_duration_str_long(self, mock_client):
        """Тест форматирования длинной длительности (более 60 минут)."""
        track = SimpleTrack.de_json(
            {"id": "1", "title": "Test", "duration": 3661, "explicit": False},
            mock_client,
        )
        # Формат MM:SS для треков > 1 часа
        assert track.get_duration_str() == "61:01"

    def test_get_artists_str(self, mock_client):
        """Тест получения строки артистов."""
        data = {
            "id": "1",
            "title": "Test",
            "duration": 100,
            "explicit": False,
            "artists": [
                {"id": "1", "title": "Artist 1", "image": None},
                {"id": "2", "title": "Artist 2", "image": None},
            ],
        }
        track = SimpleTrack.de_json(data, mock_client)
        assert track.get_artists_str() == "Artist 1, Artist 2"


class TestTrack:
    """Тесты Track."""

    def test_de_json_full(self, mock_client, sample_track_data):
        """Тест десериализации полных данных трека."""
        track = Track.de_json(sample_track_data, mock_client)

        assert track is not None
        assert track.id == "5896627"
        assert track.title == "Nothing Else Matters"
        assert track.duration == 388
        assert track.explicit is False
        assert track.has_flac is True
        assert track.position == 8
        assert len(track.artists) == 1
        assert len(track.genres) == 1
        assert track.release is not None

    def test_de_json_with_genres(self, mock_client, sample_track_data):
        """Тест десериализации с жанрами."""
        track = Track.de_json(sample_track_data, mock_client)

        assert len(track.genres) == 1
        assert track.genres[0].name == "Rock"

    def test_de_json_with_release(self, mock_client, sample_track_data):
        """Тест десериализации с релизом."""
        track = Track.de_json(sample_track_data, mock_client)

        assert track.release is not None
        assert track.release.title == "Metallica"

    def test_to_dict(self, mock_client, sample_track_data):
        """Тест сериализации в словарь."""
        track = Track.de_json(sample_track_data, mock_client)
        result = track.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "5896627"
        assert result["title"] == "Nothing Else Matters"
