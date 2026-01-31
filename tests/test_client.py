"""Тесты клиентских методов."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from zvuk_music import Client
from zvuk_music.enums import CollectionItemType, OrderBy, OrderDirection, Quality
from zvuk_music.exceptions import QualityNotAvailableError


@pytest.fixture
def client_with_mock():
    """Клиент с замоканным _request.graphql() и _request.get()."""
    with patch.object(Client, "get_anonymous_token", return_value="test_token"):
        client = Client(token="test_token")
    client._request.graphql = MagicMock()
    client._request.get = MagicMock()
    return client


class TestClientAuth:
    """Тесты авторизации."""

    def test_init_with_token(self):
        """Клиент создаётся с токеном."""
        with patch.object(Client, "get_anonymous_token", return_value="tok"):
            client = Client(token="my_token")
        assert client.token == "my_token"

    def test_is_authorized_false_by_default(self):
        """По умолчанию не авторизован."""
        with patch.object(Client, "get_anonymous_token", return_value="tok"):
            client = Client(token="tok")
        assert client.is_authorized() is False

    def test_get_profile(self, client_with_mock):
        """get_profile возвращает Profile."""
        client_with_mock._request.get = MagicMock(
            return_value={
                "id": 123,
                "token": "tok",
                "is_anonymous": False,
                "is_active": True,
            }
        )
        profile = client_with_mock.get_profile()
        assert profile is not None

    def test_init_chains(self, client_with_mock):
        """init() возвращает self для цепочки."""
        client_with_mock._request.get = MagicMock(return_value={"id": 1, "token": "t"})
        result = client_with_mock.init()
        assert result is client_with_mock

    def test_to_id_list_single_str(self):
        """_to_id_list с одной строкой."""
        assert Client._to_id_list("123") == ["123"]

    def test_to_id_list_single_int(self):
        """_to_id_list с одним int."""
        assert Client._to_id_list(123) == ["123"]

    def test_to_id_list_list(self):
        """_to_id_list со списком."""
        assert Client._to_id_list(["1", 2, "3"]) == ["1", "2", "3"]


class TestClientSearch:
    """Тесты поиска."""

    def test_quick_search(self, client_with_mock):
        """quick_search передаёт параметры и возвращает QuickSearch."""
        client_with_mock._request.graphql.return_value = {
            "quick_search": {
                "search_session_id": "sess-1",
                "content": [
                    {"__typename": "Track", "id": "1", "title": "T", "duration": 100},
                ],
            }
        }
        result = client_with_mock.quick_search("test query", limit=5)

        assert result is not None
        assert result.search_session_id == "sess-1"
        assert len(result.tracks) == 1
        client_with_mock._request.graphql.assert_called_once()

    def test_search(self, client_with_mock):
        """search возвращает Search."""
        client_with_mock._request.graphql.return_value = {
            "search": {
                "search_id": "s-1",
                "tracks": {
                    "page": {"total": 1},
                    "items": [{"id": "1", "title": "Track", "duration": 200}],
                },
            }
        }
        result = client_with_mock.search("metallica", limit=10)

        assert result is not None
        assert result.search_id == "s-1"

    def test_search_with_cursors(self, client_with_mock):
        """search передаёт курсоры."""
        client_with_mock._request.graphql.return_value = {"search": {"search_id": "s-2"}}
        client_with_mock.search("test", track_cursor="cursor1")

        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert variables["trackCursor"] == "cursor1"


class TestClientTracks:
    """Тесты треков."""

    def test_get_tracks(self, client_with_mock):
        """get_tracks возвращает список Track."""
        client_with_mock._request.graphql.return_value = {
            "get_tracks": [
                {"id": "1", "title": "Track 1", "duration": 200},
                {"id": "2", "title": "Track 2", "duration": 300},
            ]
        }
        tracks = client_with_mock.get_tracks(["1", "2"])

        assert len(tracks) == 2
        assert tracks[0].id == "1"

    def test_get_tracks_single_id(self, client_with_mock):
        """get_tracks с одним ID."""
        client_with_mock._request.graphql.return_value = {
            "get_tracks": [{"id": "1", "title": "Track 1", "duration": 200}]
        }
        tracks = client_with_mock.get_tracks("1")
        assert len(tracks) == 1

    def test_get_track(self, client_with_mock):
        """get_track возвращает один Track."""
        client_with_mock._request.graphql.return_value = {
            "get_tracks": [{"id": "5896627", "title": "Nothing Else Matters", "duration": 388}]
        }
        track = client_with_mock.get_track("5896627")

        assert track is not None
        assert track.id == "5896627"

    def test_get_track_not_found(self, client_with_mock):
        """get_track возвращает None если не найден."""
        client_with_mock._request.graphql.return_value = {"get_tracks": []}
        assert client_with_mock.get_track("999") is None

    def test_get_full_track(self, client_with_mock):
        """get_full_track передаёт withArtists и withReleases."""
        client_with_mock._request.graphql.return_value = {
            "get_tracks": [{"id": "1", "title": "T", "duration": 100}]
        }
        client_with_mock.get_full_track("1", with_artists=True, with_releases=True)

        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert variables["withArtists"] is True
        assert variables["withReleases"] is True

    def test_get_stream_urls(self, client_with_mock):
        """get_stream_urls возвращает список Stream."""
        client_with_mock._request.graphql.return_value = {
            "media_contents": [
                {
                    "stream": {
                        "expire": "2024-01-16T12:00:00",
                        "expire_delta": 86400,
                        "mid": "https://cdn.zvuk.com/stream/1",
                        "high": None,
                        "flacdrm": None,
                    }
                }
            ]
        }
        streams = client_with_mock.get_stream_urls("1")
        assert len(streams) == 1

    def test_get_stream_url(self, client_with_mock):
        """get_stream_url возвращает URL."""
        client_with_mock._request.graphql.return_value = {
            "media_contents": [
                {
                    "stream": {
                        "expire": "2024-01-16",
                        "expire_delta": 86400,
                        "mid": "https://cdn.zvuk.com/stream/1",
                        "high": None,
                        "flacdrm": None,
                    }
                }
            ]
        }
        url = client_with_mock.get_stream_url("1", Quality.MID)
        assert "cdn.zvuk.com" in url

    def test_get_stream_url_no_streams(self, client_with_mock):
        """get_stream_url вызывает ошибку если нет потоков."""
        client_with_mock._request.graphql.return_value = {"media_contents": []}
        with pytest.raises(QualityNotAvailableError):
            client_with_mock.get_stream_url("1")


class TestClientReleases:
    """Тесты релизов."""

    def test_get_releases(self, client_with_mock):
        """get_releases возвращает список Release."""
        client_with_mock._request.graphql.return_value = {
            "get_releases": [
                {"id": "669414", "title": "Metallica", "date": "1991-01-01"},
            ]
        }
        releases = client_with_mock.get_releases("669414")
        assert len(releases) == 1
        assert releases[0].id == "669414"

    def test_get_release(self, client_with_mock):
        """get_release возвращает один Release."""
        client_with_mock._request.graphql.return_value = {
            "get_releases": [{"id": "1", "title": "R"}]
        }
        release = client_with_mock.get_release("1")
        assert release is not None

    def test_get_release_not_found(self, client_with_mock):
        """get_release возвращает None если не найден."""
        client_with_mock._request.graphql.return_value = {"get_releases": []}
        assert client_with_mock.get_release("999") is None


class TestClientArtists:
    """Тесты артистов."""

    def test_get_artists(self, client_with_mock):
        """get_artists возвращает список Artist."""
        client_with_mock._request.graphql.return_value = {
            "get_artists": [
                {"id": "754367", "title": "Metallica"},
            ]
        }
        artists = client_with_mock.get_artists("754367")
        assert len(artists) == 1
        assert artists[0].title == "Metallica"

    def test_get_artists_with_flags(self, client_with_mock):
        """get_artists передаёт флаги."""
        client_with_mock._request.graphql.return_value = {"get_artists": []}
        client_with_mock.get_artists(
            "1",
            with_releases=True,
            with_popular_tracks=True,
            with_related_artists=True,
            with_description=True,
        )

        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert variables["withReleases"] is True
        assert variables["withPopTracks"] is True
        assert variables["withRelatedArtists"] is True
        assert variables["withDescription"] is True

    def test_get_artist(self, client_with_mock):
        """get_artist возвращает одного Artist."""
        client_with_mock._request.graphql.return_value = {
            "get_artists": [{"id": "1", "title": "A"}]
        }
        artist = client_with_mock.get_artist("1")
        assert artist is not None

    def test_get_artist_not_found(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"get_artists": []}
        assert client_with_mock.get_artist("999") is None


class TestClientPlaylists:
    """Тесты плейлистов."""

    def test_get_playlist(self, client_with_mock):
        """get_playlist возвращает Playlist."""
        client_with_mock._request.graphql.return_value = {
            "get_playlists": [{"id": "12345", "title": "My Playlist"}]
        }
        playlist = client_with_mock.get_playlist("12345")
        assert playlist is not None
        assert playlist.id == "12345"

    def test_get_playlists(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {
            "get_playlists": [
                {"id": "1", "title": "P1"},
                {"id": "2", "title": "P2"},
            ]
        }
        playlists = client_with_mock.get_playlists(["1", "2"])
        assert len(playlists) == 2

    def test_create_playlist(self, client_with_mock):
        """create_playlist возвращает ID."""
        client_with_mock._request.graphql.return_value = {"playlist": {"create": "new-id-123"}}
        result = client_with_mock.create_playlist("New Playlist")
        assert result == "new-id-123"

    def test_create_playlist_with_tracks(self, client_with_mock):
        """create_playlist с треками."""
        client_with_mock._request.graphql.return_value = {"playlist": {"create": "new-id"}}
        client_with_mock.create_playlist("PL", track_ids=["t1", "t2"])

        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert len(variables["items"]) == 2
        assert variables["items"][0]["type"] == "track"

    def test_delete_playlist(self, client_with_mock):
        """delete_playlist возвращает True."""
        client_with_mock._request.graphql.return_value = {"playlist": {"delete": True}}
        assert client_with_mock.delete_playlist("12345") is True

    def test_rename_playlist(self, client_with_mock):
        """rename_playlist возвращает True."""
        client_with_mock._request.graphql.return_value = {"playlist": {"rename": True}}
        assert client_with_mock.rename_playlist("12345", "New Name") is True

    def test_add_tracks_to_playlist(self, client_with_mock):
        """add_tracks_to_playlist возвращает True."""
        client_with_mock._request.graphql.return_value = {"playlist": {"add_items": True}}
        assert client_with_mock.add_tracks_to_playlist("12345", ["t1", "t2"]) is True

    def test_update_playlist(self, client_with_mock):
        """update_playlist возвращает True."""
        client_with_mock._request.graphql.return_value = {"playlist": {"update": True}}
        result = client_with_mock.update_playlist("12345", ["t1"], name="Updated")
        assert result is True

    def test_set_playlist_public(self, client_with_mock):
        """set_playlist_public возвращает True."""
        client_with_mock._request.graphql.return_value = {"playlist": {"set_public": True}}
        assert client_with_mock.set_playlist_public("12345", True) is True

    def test_get_playlist_tracks(self, client_with_mock):
        """get_playlist_tracks возвращает список SimpleTrack."""
        client_with_mock._request.graphql.return_value = {
            "playlist_tracks": [
                {"id": "1", "title": "T1", "duration": 100},
            ]
        }
        tracks = client_with_mock.get_playlist_tracks("12345", limit=10, offset=0)
        assert len(tracks) == 1


class TestClientPodcasts:
    """Тесты подкастов."""

    def test_get_podcast(self, client_with_mock):
        """get_podcast возвращает Podcast."""
        client_with_mock._request.graphql.return_value = {
            "get_podcasts": [{"id": "7001", "title": "Pod"}]
        }
        podcast = client_with_mock.get_podcast("7001")
        assert podcast is not None
        assert podcast.id == "7001"

    def test_get_podcasts(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {
            "get_podcasts": [{"id": "1", "title": "P1"}]
        }
        podcasts = client_with_mock.get_podcasts("1")
        assert len(podcasts) == 1

    def test_get_episode(self, client_with_mock):
        """get_episode возвращает Episode."""
        client_with_mock._request.graphql.return_value = {
            "get_episodes": [{"id": "8001", "title": "Ep1", "duration": 1800}]
        }
        episode = client_with_mock.get_episode("8001")
        assert episode is not None
        assert episode.id == "8001"

    def test_get_episodes(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {
            "get_episodes": [{"id": "1", "title": "E1", "duration": 600}]
        }
        episodes = client_with_mock.get_episodes(["1"])
        assert len(episodes) == 1


class TestClientCollection:
    """Тесты коллекции."""

    def test_get_collection(self, client_with_mock):
        """get_collection возвращает Collection."""
        client_with_mock._request.graphql.return_value = {
            "collection": {
                "tracks": [{"id": "1", "item_status": "liked"}],
                "artists": [],
            }
        }
        collection = client_with_mock.get_collection()
        assert collection is not None
        assert len(collection.tracks) == 1

    def test_get_liked_tracks(self, client_with_mock):
        """get_liked_tracks возвращает список Track."""
        client_with_mock._request.graphql.return_value = {
            "collection": {"tracks": [{"id": "1", "title": "T", "duration": 100}]}
        }
        tracks = client_with_mock.get_liked_tracks()
        assert len(tracks) == 1

    def test_get_liked_tracks_with_sort(self, client_with_mock):
        """get_liked_tracks передаёт параметры сортировки."""
        client_with_mock._request.graphql.return_value = {"collection": {"tracks": []}}
        client_with_mock.get_liked_tracks(
            order_by=OrderBy.ALPHABET,
            direction=OrderDirection.ASC,
        )
        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert variables["orderBy"] == "alphabet"
        assert variables["orderDirection"] == "asc"

    def test_like_track(self, client_with_mock):
        """like_track возвращает True."""
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        assert client_with_mock.like_track("1") is True

    def test_unlike_track(self, client_with_mock):
        """unlike_track возвращает True."""
        client_with_mock._request.graphql.return_value = {"collection": {"remove_item": True}}
        assert client_with_mock.unlike_track("1") is True

    def test_add_to_collection(self, client_with_mock):
        """add_to_collection передаёт тип."""
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        result = client_with_mock.add_to_collection("1", CollectionItemType.RELEASE)
        assert result is True

        call_args = client_with_mock._request.graphql.call_args
        variables = call_args[0][2]
        assert variables["type"] == "release"

    def test_remove_from_collection(self, client_with_mock):
        """remove_from_collection передаёт тип."""
        client_with_mock._request.graphql.return_value = {"collection": {"remove_item": True}}
        result = client_with_mock.remove_from_collection("1", CollectionItemType.TRACK)
        assert result is True

    def test_like_release(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        assert client_with_mock.like_release("1") is True

    def test_like_artist(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        assert client_with_mock.like_artist("1") is True

    def test_like_playlist(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        assert client_with_mock.like_playlist("1") is True

    def test_like_podcast(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"collection": {"add_item": True}}
        assert client_with_mock.like_podcast("1") is True


class TestClientHidden:
    """Тесты скрытых элементов."""

    def test_get_hidden_collection(self, client_with_mock):
        """get_hidden_collection возвращает HiddenCollection."""
        client_with_mock._request.graphql.return_value = {
            "hidden_collection": {
                "tracks": [{"id": "1", "item_status": "liked"}],
                "artists": [],
            }
        }
        hidden = client_with_mock.get_hidden_collection()
        assert hidden is not None
        assert len(hidden.tracks) == 1

    def test_hide_track(self, client_with_mock):
        """hide_track возвращает True."""
        client_with_mock._request.graphql.return_value = {"hidden_collection": {"add_item": True}}
        assert client_with_mock.hide_track("1") is True

    def test_unhide_track(self, client_with_mock):
        """unhide_track возвращает True."""
        client_with_mock._request.graphql.return_value = {
            "hidden_collection": {"remove_item": True}
        }
        assert client_with_mock.unhide_track("1") is True

    def test_get_hidden_tracks(self, client_with_mock):
        """get_hidden_tracks возвращает список CollectionItem."""
        client_with_mock._request.graphql.return_value = {
            "hidden_collection": {"tracks": [{"id": "1"}, {"id": "2"}]}
        }
        tracks = client_with_mock.get_hidden_tracks()
        assert len(tracks) == 2


class TestClientProfiles:
    """Тесты профилей."""

    def test_get_profile_followers_count(self, client_with_mock):
        """get_profile_followers_count возвращает список чисел."""
        client_with_mock._request.graphql.return_value = {
            "profiles": [
                {"collection_item_data": {"likes_count": 100}},
                {"collection_item_data": {"likes_count": 200}},
            ]
        }
        counts = client_with_mock.get_profile_followers_count(["1", "2"])
        assert counts == [100, 200]

    def test_get_following_count(self, client_with_mock):
        """get_following_count возвращает число."""
        client_with_mock._request.graphql.return_value = {"follows": {"followings": {"count": 42}}}
        count = client_with_mock.get_following_count("1")
        assert count == 42


class TestClientHistory:
    """Тесты истории."""

    def test_get_listening_history(self, client_with_mock):
        """get_listening_history возвращает список."""
        client_with_mock._request.graphql.return_value = {
            "listening_history": [{"track_id": "1"}, {"track_id": "2"}]
        }
        history = client_with_mock.get_listening_history()
        assert len(history) == 2

    def test_get_listened_episodes(self, client_with_mock):
        """get_listened_episodes возвращает список."""
        client_with_mock._request.graphql.return_value = {
            "get_play_state": {"episodes": [{"id": "1"}]}
        }
        episodes = client_with_mock.get_listened_episodes()
        assert len(episodes) == 1

    def test_has_unread_notifications(self, client_with_mock):
        """has_unread_notifications возвращает bool."""
        client_with_mock._request.graphql.return_value = {"notification": {"has_unread": True}}
        assert client_with_mock.has_unread_notifications() is True

    def test_has_no_unread_notifications(self, client_with_mock):
        client_with_mock._request.graphql.return_value = {"notification": {"has_unread": False}}
        assert client_with_mock.has_unread_notifications() is False


class TestClientSynthesis:
    """Тесты синтез-плейлистов."""

    def test_synthesis_playlist_build(self, client_with_mock):
        """synthesis_playlist_build возвращает SynthesisPlaylist."""
        client_with_mock._request.graphql.return_value = {
            "synthesis_playlist_build": {
                "id": "synth-1",
                "tracks": [{"id": "1", "title": "T", "duration": 100}],
                "authors": [{"id": "a1", "name": "Author 1", "image": None}],
            }
        }
        sp = client_with_mock.synthesis_playlist_build("auth1", "auth2")
        assert sp is not None
        assert sp.id == "synth-1"

    def test_get_synthesis_playlists(self, client_with_mock):
        """get_synthesis_playlists возвращает список."""
        client_with_mock._request.graphql.return_value = {
            "synthesis_playlist": [{"id": "s1"}, {"id": "s2"}]
        }
        result = client_with_mock.get_synthesis_playlists(["s1", "s2"])
        assert len(result) == 2


class TestClientUserCollections:
    """Тесты пользовательских коллекций."""

    def test_get_user_playlists(self, client_with_mock):
        """get_user_playlists возвращает список CollectionItem."""
        client_with_mock._request.graphql.return_value = {
            "collection": {"playlists": [{"id": "1", "item_status": "liked"}]}
        }
        playlists = client_with_mock.get_user_playlists()
        assert len(playlists) == 1

    def test_get_short_playlist(self, client_with_mock):
        """get_short_playlist возвращает SimplePlaylist."""
        client_with_mock._request.graphql.return_value = {
            "get_playlists": [{"id": "1", "title": "PL"}]
        }
        playlists = client_with_mock.get_short_playlist("1")
        assert len(playlists) == 1

    def test_get_user_paginated_podcasts(self, client_with_mock):
        """get_user_paginated_podcasts возвращает dict."""
        client_with_mock._request.graphql.return_value = {
            "paginated_collection": {"items": [], "cursor": "next"}
        }
        result = client_with_mock.get_user_paginated_podcasts(count=10)
        assert isinstance(result, dict)
