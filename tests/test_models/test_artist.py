"""Tests for Artist model."""

import pytest

from zvuk_music.models.artist import Artist, SimpleArtist


class TestSimpleArtist:
    """Tests for SimpleArtist."""

    def test_de_json_valid(self, mock_client):
        """Test deserialization of valid data."""
        data = {
            "id": "754367",
            "title": "Metallica",
            "image": {"src": "https://example.com/image.jpg"},
        }
        artist = SimpleArtist.de_json(data, mock_client)

        assert artist is not None
        assert artist.id == "754367"
        assert artist.title == "Metallica"
        assert artist.image is not None
        assert artist.image.src == "https://example.com/image.jpg"

    def test_de_json_none(self, mock_client):
        """Test deserialization of None."""
        artist = SimpleArtist.de_json(None, mock_client)
        assert artist is None

    def test_de_json_empty_dict(self, mock_client):
        """Test deserialization of empty dict returns None."""
        artist = SimpleArtist.de_json({}, mock_client)
        # Empty dict is not valid data
        assert artist is None

    def test_de_list(self, mock_client):
        """Test deserialization of a list."""
        data = [
            {"id": "1", "title": "Artist 1", "image": None},
            {"id": "2", "title": "Artist 2", "image": None},
        ]
        artists = SimpleArtist.de_list(data, mock_client)

        assert len(artists) == 2
        assert artists[0].id == "1"
        assert artists[1].id == "2"

    def test_equality(self, mock_client):
        """Test artist comparison."""
        artist1 = SimpleArtist.de_json({"id": "1", "title": "Artist", "image": None}, mock_client)
        artist2 = SimpleArtist.de_json({"id": "1", "title": "Artist", "image": None}, mock_client)
        artist3 = SimpleArtist.de_json({"id": "2", "title": "Artist", "image": None}, mock_client)

        assert artist1 == artist2
        assert artist1 != artist3


class TestArtist:
    """Tests for Artist."""

    def test_de_json_full(self, mock_client, sample_artist_data):
        """Test deserialization of full artist data."""
        artist = Artist.de_json(sample_artist_data, mock_client)

        assert artist is not None
        assert artist.id == "754367"
        assert artist.title == "Metallica"
        assert artist.description == "Metallica – американская метал-группа."
        assert artist.has_page is True

    def test_de_json_with_releases(self, mock_client):
        """Test deserialization with releases."""
        data = {
            "id": "754367",
            "title": "Metallica",
            "image": None,
            "releases": [
                {
                    "id": "669414",
                    "title": "Metallica",
                    "date": "1991-01-01",
                    "type": "album",
                    "image": None,
                    "explicit": False,
                    "artists": [],
                }
            ],
            "popular_tracks": [],
            "related_artists": [],
        }
        artist = Artist.de_json(data, mock_client)

        assert len(artist.releases) == 1
        assert artist.releases[0].title == "Metallica"

    def test_de_json_with_popular_tracks(self, mock_client):
        """Test deserialization with popular tracks."""
        data = {
            "id": "754367",
            "title": "Metallica",
            "image": None,
            "releases": [],
            "popular_tracks": [
                {
                    "id": "5896627",
                    "title": "Nothing Else Matters",
                    "duration": 388,
                    "explicit": False,
                    "artists": [],
                    "release": None,
                }
            ],
            "related_artists": [],
        }
        artist = Artist.de_json(data, mock_client)

        assert len(artist.popular_tracks) == 1
        assert artist.popular_tracks[0].title == "Nothing Else Matters"

    def test_to_dict(self, mock_client, sample_artist_data):
        """Test serialization to dictionary."""
        artist = Artist.de_json(sample_artist_data, mock_client)
        result = artist.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "754367"
        assert result["title"] == "Metallica"
