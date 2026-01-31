"""Tests for Track model."""

import pytest

from zvuk_music.models.track import SimpleTrack, Track


class TestSimpleTrack:
    """Tests for SimpleTrack."""

    def test_de_json_valid(self, mock_client):
        """Test deserialization of valid data."""
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
        """Test deserialization of None."""
        track = SimpleTrack.de_json(None, mock_client)
        assert track is None

    def test_de_json_empty_dict(self, mock_client):
        """Test deserialization of empty dict returns None."""
        track = SimpleTrack.de_json({}, mock_client)
        # Empty dict is not valid track data
        assert track is None

    def test_de_list(self, mock_client):
        """Test deserialization of a list."""
        data = [
            {"id": "1", "title": "Track 1", "duration": 100, "explicit": False},
            {"id": "2", "title": "Track 2", "duration": 200, "explicit": True},
        ]
        tracks = SimpleTrack.de_list(data, mock_client)

        assert len(tracks) == 2
        assert tracks[0].id == "1"
        assert tracks[1].id == "2"

    def test_get_duration_str(self, mock_client):
        """Test duration formatting."""
        track = SimpleTrack.de_json(
            {"id": "1", "title": "Test", "duration": 185, "explicit": False},
            mock_client,
        )
        assert track.get_duration_str() == "3:05"

    def test_get_duration_str_long(self, mock_client):
        """Test long duration formatting (over 60 minutes)."""
        track = SimpleTrack.de_json(
            {"id": "1", "title": "Test", "duration": 3661, "explicit": False},
            mock_client,
        )
        # MM:SS format for tracks > 1 hour
        assert track.get_duration_str() == "61:01"

    def test_get_artists_str(self, mock_client):
        """Test getting artists string."""
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
    """Tests for Track."""

    def test_de_json_full(self, mock_client, sample_track_data):
        """Test deserialization of full track data."""
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
        """Test deserialization with genres."""
        track = Track.de_json(sample_track_data, mock_client)

        assert len(track.genres) == 1
        assert track.genres[0].name == "Rock"

    def test_de_json_with_release(self, mock_client, sample_track_data):
        """Test deserialization with release."""
        track = Track.de_json(sample_track_data, mock_client)

        assert track.release is not None
        assert track.release.title == "Metallica"

    def test_to_dict(self, mock_client, sample_track_data):
        """Test serialization to dictionary."""
        track = Track.de_json(sample_track_data, mock_client)
        result = track.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "5896627"
        assert result["title"] == "Nothing Else Matters"
