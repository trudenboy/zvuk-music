"""Tests for Search model."""

import pytest

from zvuk_music.models.search import QuickSearch, Search, SearchResult


class TestQuickSearch:
    """Tests for QuickSearch."""

    def test_de_json_with_content_array(self, mock_client, sample_quick_search_data):
        """Test deserialization with content array."""
        result = QuickSearch.de_json(sample_quick_search_data, mock_client)

        assert result is not None
        assert result.search_session_id == "test-session-id"
        assert len(result.artists) == 1
        assert len(result.tracks) == 1
        assert result.artists[0].title == "Metallica"
        assert result.tracks[0].title == "Nothing Else Matters"

    def test_de_json_none(self, mock_client):
        """Test deserialization of None."""
        result = QuickSearch.de_json(None, mock_client)
        assert result is None

    def test_de_json_empty_content(self, mock_client):
        """Test deserialization with empty content."""
        data = {"search_session_id": "test", "content": []}
        result = QuickSearch.de_json(data, mock_client)

        assert result is not None
        assert result.search_session_id == "test"
        assert len(result.tracks) == 0
        assert len(result.artists) == 0

    def test_de_json_mixed_types(self, mock_client):
        """Test deserialization with mixed types in content."""
        data = {
            "search_session_id": "test",
            "content": [
                {"__typename": "Artist", "id": "1", "title": "Artist 1", "image": None},
                {
                    "__typename": "Track",
                    "id": "2",
                    "title": "Track 1",
                    "duration": 100,
                    "explicit": False,
                    "artists": [],
                    "release": None,
                },
                {
                    "__typename": "Release",
                    "id": "3",
                    "title": "Release 1",
                    "date": None,
                    "type": None,
                    "image": None,
                    "explicit": False,
                    "artists": [],
                },
                {
                    "__typename": "Playlist",
                    "id": "4",
                    "title": "Playlist 1",
                    "is_public": True,
                    "description": None,
                    "duration": 0,
                    "image": None,
                },
            ],
        }
        result = QuickSearch.de_json(data, mock_client)

        assert len(result.artists) == 1
        assert len(result.tracks) == 1
        assert len(result.releases) == 1
        assert len(result.playlists) == 1

    def test_default_empty_lists(self, mock_client):
        """Test default empty lists."""
        data = {"search_session_id": "test"}
        result = QuickSearch.de_json(data, mock_client)

        assert result.tracks == []
        assert result.artists == []
        assert result.releases == []
        assert result.playlists == []
        assert result.profiles == []
        assert result.books == []
        assert result.episodes == []
        assert result.podcasts == []


class TestSearchResult:
    """Tests for SearchResult."""

    def test_de_json_with_type_tracks(self, mock_client):
        """Test deserialization of track search results."""
        from zvuk_music.models.track import SimpleTrack

        data = {
            "page": {"total": 100, "prev": None, "next": 2, "cursor": "abc123"},
            "score": 0.95,
            "items": [
                {
                    "id": "1",
                    "title": "Track 1",
                    "duration": 100,
                    "explicit": False,
                    "artists": [],
                    "release": None,
                },
                {
                    "id": "2",
                    "title": "Track 2",
                    "duration": 200,
                    "explicit": True,
                    "artists": [],
                    "release": None,
                },
            ],
        }
        result = SearchResult.de_json_with_type(data, mock_client, SimpleTrack)

        assert result is not None
        assert result.page.total == 100
        assert result.score == 0.95
        assert len(result.items) == 2
        assert result.items[0].title == "Track 1"

    def test_page_has_next(self, mock_client):
        """Test checking for next page."""
        from zvuk_music.models.search import Page

        page_with_next = Page.de_json({"next": 2, "total": 100}, mock_client)
        page_with_cursor = Page.de_json({"cursor": "abc", "total": 100}, mock_client)
        # Empty dict returns None
        page_without_next = Page.de_json({"total": 0}, mock_client)

        assert page_with_next.has_next() is True
        assert page_with_cursor.has_next() is True
        assert page_without_next.has_next() is False
