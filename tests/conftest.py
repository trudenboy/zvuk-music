"""Pytest fixtures for Zvuk Music API tests."""

import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from zvuk_music import Client


@pytest.fixture
def mock_client() -> Client:
    """Create a mock client without making real requests."""
    with patch.object(Client, "get_anonymous_token", return_value="test_token"):
        client = Client(token="test_token")
    return client


@pytest.fixture
def sample_track_data() -> Dict[str, Any]:
    """Sample track data from API."""
    return {
        "id": "5896627",
        "title": "Nothing Else Matters",
        "search_title": "Nothing Else Matters",
        "position": 8,
        "duration": 388,
        "availability": 2,
        "artist_template": "{0}",
        "condition": None,
        "explicit": False,
        "lyrics": None,
        "zchan": None,
        "has_flac": True,
        "artist_names": ["Metallica"],
        "credits": None,
        "genres": [{"id": "23", "name": "Rock", "short_name": ""}],
        "artists": [
            {
                "id": "754367",
                "title": "Metallica",
                "image": {
                    "src": "https://cdn-image.zvuk.com/pic?id=754367&size={size}&type=artist"
                },
            }
        ],
        "release": {
            "id": "669414",
            "title": "Metallica",
            "date": "1991-01-01T00:00:00",
            "type": "album",
            "image": {"src": "https://cdn-image.zvuk.com/pic?id=669414&size={size}&type=release"},
            "explicit": False,
            "artists": [{"id": "754367", "title": "Metallica", "image": None}],
        },
        "collection_item_data": {
            "id": None,
            "user_id": None,
            "item_status": None,
            "last_modified": None,
            "collection_last_modified": None,
            "likes_count": None,
        },
    }


@pytest.fixture
def sample_artist_data() -> Dict[str, Any]:
    """Sample artist data from API."""
    return {
        "id": "754367",
        "title": "Metallica",
        "image": {"src": "https://cdn-image.zvuk.com/pic?id=754367&size={size}&type=artist"},
        "second_image": None,
        "search_title": "Metallica",
        "description": "Metallica – американская метал-группа.",
        "has_page": True,
        "animation": None,
        "collection_item_data": None,
        "releases": [],
        "popular_tracks": [],
        "related_artists": [],
    }


@pytest.fixture
def sample_release_data() -> Dict[str, Any]:
    """Sample release data from API."""
    return {
        "id": "669414",
        "title": "Metallica",
        "search_title": "Metallica",
        "date": "1991-01-01T00:00:00",
        "type": "album",
        "image": {"src": "https://cdn-image.zvuk.com/pic?id=669414&size={size}&type=release"},
        "explicit": False,
        "availability": 2,
        "artist_template": "{0}",
        "genres": [{"id": "23", "name": "Rock", "short_name": ""}],
        "label": {"id": "114338", "title": "EMI"},
        "artists": [{"id": "754367", "title": "Metallica", "image": None}],
        "tracks": [],
        "related": [],
        "collection_item_data": None,
    }


@pytest.fixture
def sample_stream_data() -> Dict[str, Any]:
    """Sample stream data from API."""
    return {
        "expire": "2024-01-16T12:00:00",
        "expire_delta": 86400,
        "mid": "https://cdn66.zvuk.com/track/5896627/stream?mid=1",
        "high": None,
        "flacdrm": None,
    }


@pytest.fixture
def sample_quick_search_data() -> Dict[str, Any]:
    """Sample quick search response from API."""
    return {
        "search_session_id": "test-session-id",
        "content": [
            {
                "__typename": "Artist",
                "id": "754367",
                "title": "Metallica",
                "image": {"src": "https://cdn-image.zvuk.com/pic"},
            },
            {
                "__typename": "Track",
                "id": "5896627",
                "title": "Nothing Else Matters",
                "duration": 388,
                "explicit": False,
                "artists": [{"id": "754367", "title": "Metallica", "image": None}],
                "release": None,
            },
        ],
    }


@pytest.fixture
def sample_profile_data() -> Dict[str, Any]:
    """Sample profile data from API."""
    return {
        "id": 123456789,
        "token": "test_token_123",
        "is_anonymous": True,
        "allow_explicit": True,
        "birthday": None,
        "created": 1700000000,
        "email": None,
        "external_profile": None,
        "gender": None,
        "image": None,
        "is_active": True,
        "is_agreement": True,
        "is_editor": False,
        "is_registered": False,
        "name": None,
        "phone": None,
        "registered": None,
        "username": None,
    }


@pytest.fixture
def sample_playlist_data() -> Dict[str, Any]:
    """Sample playlist data from API."""
    return {
        "id": "12345",
        "title": "My Playlist",
        "user_id": "999",
        "is_public": True,
        "is_deleted": False,
        "shared": False,
        "branded": False,
        "description": "Test playlist",
        "duration": 1200,
        "image": {"src": "https://cdn-image.zvuk.com/pic?id=12345&size={size}&type=playlist"},
        "updated": "2024-01-01T00:00:00",
        "search_title": "My Playlist",
        "tracks": [
            {
                "id": "5896627",
                "title": "Nothing Else Matters",
                "duration": 388,
                "explicit": False,
                "artists": [{"id": "754367", "title": "Metallica", "image": None}],
                "release": None,
            }
        ],
    }


@pytest.fixture
def sample_podcast_data() -> Dict[str, Any]:
    """Sample podcast data from API."""
    return {
        "id": "7001",
        "title": "Tech Podcast",
        "explicit": False,
        "description": "A tech podcast",
        "updated_date": "2024-01-15T10:00:00",
        "availability": 2,
        "type": "podcast",
        "image": {"src": "https://cdn-image.zvuk.com/pic?id=7001&size={size}&type=podcast"},
        "authors": [{"id": "1001", "name": "Host Name"}],
        "episodes": [{"id": "8001"}, {"id": "8002"}],
        "collection_item_data": None,
    }


@pytest.fixture
def sample_collection_data() -> Dict[str, Any]:
    """Sample collection data from API."""
    return {
        "artists": [
            {"id": "1", "user_id": "100", "item_status": "liked"},
        ],
        "episodes": [],
        "podcasts": [],
        "playlists": [],
        "synthesis_playlists": [],
        "profiles": [],
        "releases": [
            {"id": "2", "user_id": "100", "item_status": "liked"},
        ],
        "tracks": [
            {"id": "3", "user_id": "100", "item_status": "liked"},
            {"id": "4", "user_id": "100", "item_status": "liked"},
        ],
    }
