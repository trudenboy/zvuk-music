"""Тесты моделей плейлиста."""

from zvuk_music.models.playlist import (
    Playlist,
    PlaylistAuthor,
    PlaylistItem,
    SimplePlaylist,
    SynthesisPlaylist,
)


class TestPlaylistItem:
    """Тесты PlaylistItem."""

    def test_defaults(self, mock_client):
        item = PlaylistItem(client=mock_client, type="track", item_id="123")
        assert item.type == "track"
        assert item.item_id == "123"


class TestSimplePlaylist:
    """Тесты SimplePlaylist."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "12345",
            "title": "My Playlist",
            "is_public": True,
            "description": "desc",
            "duration": 600,
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
        }
        playlist = SimplePlaylist.de_json(data, mock_client)

        assert playlist is not None
        assert playlist.id == "12345"
        assert playlist.title == "My Playlist"
        assert playlist.is_public is True
        assert playlist.image is not None

    def test_de_json_none(self, mock_client):
        assert SimplePlaylist.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert SimplePlaylist.de_json({}, mock_client) is None

    def test_de_list(self, mock_client):
        data = [
            {"id": "1", "title": "Playlist 1"},
            {"id": "2", "title": "Playlist 2"},
        ]
        playlists = SimplePlaylist.de_list(data, mock_client)
        assert len(playlists) == 2


class TestPlaylist:
    """Тесты Playlist."""

    def test_de_json_full(self, mock_client, sample_playlist_data):
        playlist = Playlist.de_json(sample_playlist_data, mock_client)

        assert playlist is not None
        assert playlist.id == "12345"
        assert playlist.title == "My Playlist"
        assert playlist.user_id == "999"
        assert playlist.is_public is True
        assert playlist.is_deleted is False
        assert playlist.duration == 1200
        assert playlist.image is not None
        assert len(playlist.tracks) == 1
        assert playlist.tracks[0].title == "Nothing Else Matters"

    def test_de_json_none(self, mock_client):
        assert Playlist.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert Playlist.de_json({}, mock_client) is None

    def test_default_empty_tracks(self, mock_client):
        playlist = Playlist.de_json({"id": "1", "title": "Test"}, mock_client)
        assert playlist.tracks == []

    def test_to_dict(self, mock_client, sample_playlist_data):
        playlist = Playlist.de_json(sample_playlist_data, mock_client)
        d = playlist.to_dict()
        assert isinstance(d, dict)
        assert d["id"] == "12345"
        assert "client" not in d


class TestPlaylistAuthor:
    """Тесты PlaylistAuthor."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "100",
            "name": "DJ Mix",
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
            "matches": 0.95,
        }
        author = PlaylistAuthor.de_json(data, mock_client)
        assert author is not None
        assert author.id == "100"
        assert author.name == "DJ Mix"
        assert author.matches == 0.95

    def test_de_json_none(self, mock_client):
        assert PlaylistAuthor.de_json(None, mock_client) is None


class TestSynthesisPlaylist:
    """Тесты SynthesisPlaylist."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "synth-1",
            "tracks": [
                {"id": "1", "title": "Track 1", "duration": 200, "explicit": False},
            ],
            "authors": [
                {"id": "100", "name": "Author 1", "image": None},
            ],
        }
        sp = SynthesisPlaylist.de_json(data, mock_client)

        assert sp is not None
        assert sp.id == "synth-1"
        assert len(sp.tracks) == 1
        assert len(sp.authors) == 1

    def test_de_json_none(self, mock_client):
        assert SynthesisPlaylist.de_json(None, mock_client) is None

    def test_default_empty_lists(self, mock_client):
        sp = SynthesisPlaylist.de_json({"id": "1"}, mock_client)
        assert sp.tracks == []
        assert sp.authors == []
