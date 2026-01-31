"""Synchronous Zvuk Music API client.

Note (RU): Синхронный клиент Zvuk Music API.
"""

from typing import Any, Dict, List, Optional, Union

import requests

from zvuk_music.enums import CollectionItemType, OrderBy, OrderDirection, Quality
from zvuk_music.exceptions import QualityNotAvailableError
from zvuk_music.models.artist import Artist
from zvuk_music.models.collection import Collection, CollectionItem, HiddenCollection
from zvuk_music.models.playlist import Playlist, SimplePlaylist, SimpleTrack, SynthesisPlaylist
from zvuk_music.models.podcast import Episode, Podcast
from zvuk_music.models.profile import Profile, ProfileResult
from zvuk_music.models.release import Release
from zvuk_music.models.search import QuickSearch, Search
from zvuk_music.models.stream import Stream
from zvuk_music.models.track import Track
from zvuk_music.utils.graphql import load_query
from zvuk_music.utils.request import TINY_API_URL, Request


class Client:
    """Synchronous Zvuk Music API client.

    Args:
        token: Authorization token (obtain via get_anonymous_token() or from browser).
        timeout: Request timeout in seconds.
        proxy_url: Proxy server URL.
        user_agent: User-Agent for requests (important for bypassing bot protection).
        report_unknown_fields: Log unknown fields from API.

    Example:
        >>> # Anonymous access (limited functionality):
        >>> token = Client.get_anonymous_token()
        >>> client = Client(token=token)
        >>>
        >>> # Authorized access (full functionality):
        >>> # 1. Log in to zvuk.com in browser
        >>> # 2. Open https://zvuk.com/api/tiny/profile
        >>> # 3. Copy the "token" field value
        >>> client = Client(token="your_token")

    Note (RU): Синхронный клиент Zvuk Music API.
    """

    @staticmethod
    def _to_id_list(ids: Union[str, int, List[Union[str, int]]]) -> List[str]:
        """Normalize IDs to a list of strings.

        Args:
            ids: ID or list of IDs.

        Returns:
            List of string IDs.

        Note (RU): Нормализация ID в список строк.
        """
        if not isinstance(ids, list):
            ids = [ids]
        return [str(i) for i in ids]

    def __init__(
        self,
        token: Optional[str] = None,
        timeout: float = 10.0,
        proxy_url: Optional[str] = None,
        user_agent: Optional[str] = None,
        report_unknown_fields: bool = False,
    ) -> None:
        self.token = token or ""
        self.report_unknown_fields = report_unknown_fields

        self._request = Request(
            client=self,
            proxy_url=proxy_url,
            timeout=timeout,
        )

        if user_agent:
            self._request.set_user_agent(user_agent)

        if self.token:
            self._request.set_authorization(self.token)

        self._profile: Optional[ProfileResult] = None

    @staticmethod
    def get_anonymous_token() -> str:
        """Get an anonymous token.

        Anonymous token provides limited access:
        - Only mid quality (128kbps)
        - No access to collection
        - No ability to like

        Returns:
            Anonymous token.

        Note (RU): Получить анонимный токен.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://zvuk.com/",
            "Origin": "https://zvuk.com",
        }
        response = requests.get(f"{TINY_API_URL}/profile", headers=headers)
        response.raise_for_status()
        data = response.json()
        return str(data["result"]["token"])

    def init(self) -> "Client":
        """Initialize the client, load profile.

        Returns:
            self for method chaining.

        Note (RU): Инициализировать клиент, загрузить профиль.
        """
        self.get_profile()
        return self

    def get_profile(self) -> Optional[Profile]:
        """Get the current user's profile.

        Returns:
            User profile.

        Note (RU): Получить профиль текущего пользователя.
        """
        data = self._request.get(f"{TINY_API_URL}/profile")
        # Request.get already returns result, wrap back for Profile
        profile = Profile.de_json({"result": data}, self)
        if profile and profile.result:
            self._profile = profile.result
        return profile

    def is_authorized(self) -> bool:
        """Check if the user is authorized (not anonymous).

        Returns:
            True if authorized.

        Note (RU): Авторизован ли пользователь (не анонимный).
        """
        if self._profile:
            return self._profile.is_authorized()
        return False

    # ========== Search ==========

    def quick_search(
        self,
        query: str,
        limit: int = 10,
        search_session_id: Optional[str] = None,
    ) -> Optional[QuickSearch]:
        """Quick search with autocomplete.

        Args:
            query: Search query.
            limit: Maximum results.
            search_session_id: Search session ID.

        Returns:
            Quick search results.

        Note (RU): Быстрый поиск с автодополнением.
        """
        gql = load_query("quickSearch")
        variables: Dict[str, Any] = {"query": query, "limit": limit}
        if search_session_id:
            variables["searchSessionId"] = search_session_id

        result = self._request.graphql(gql, "quickSearch", variables)
        # API returns quick_search (snake_case after normalization)
        data = result.get("quick_search") or result.get("quickSearch") or {}
        return QuickSearch.de_json(data, self)

    def search(
        self,
        query: str,
        limit: int = 20,
        tracks: bool = True,
        artists: bool = True,
        releases: bool = True,
        playlists: bool = True,
        podcasts: bool = True,
        episodes: bool = True,
        profiles: bool = True,
        books: bool = True,
        track_cursor: Optional[str] = None,
        artist_cursor: Optional[str] = None,
        release_cursor: Optional[str] = None,
        playlist_cursor: Optional[str] = None,
    ) -> Optional[Search]:
        """Full-text search.

        Args:
            query: Search query.
            limit: Maximum results per category.
            tracks: Search tracks.
            artists: Search artists.
            releases: Search releases.
            playlists: Search playlists.
            podcasts: Search podcasts.
            episodes: Search episodes.
            profiles: Search profiles.
            books: Search books.
            track_cursor: Cursor for tracks.
            artist_cursor: Cursor for artists.
            release_cursor: Cursor for releases.
            playlist_cursor: Cursor for playlists.

        Returns:
            Search results.

        Note (RU): Полнотекстовый поиск.
        """
        gql = load_query("search")
        variables: Dict[str, Any] = {
            "query": query,
            "limit": limit,
            "withTracks": tracks,
            "withArtists": artists,
            "withReleases": releases,
            "withPlaylists": playlists,
            "withPodcasts": podcasts,
            "withEpisodes": episodes,
            "withProfiles": profiles,
            "withBooks": books,
        }

        if track_cursor:
            variables["trackCursor"] = track_cursor
        if artist_cursor:
            variables["artistCursor"] = artist_cursor
        if release_cursor:
            variables["releaseCursor"] = release_cursor
        if playlist_cursor:
            variables["playlistCursor"] = playlist_cursor

        result = self._request.graphql(gql, "search", variables)
        return Search.de_json(result.get("search", {}), self)

    # ========== Tracks ==========

    def get_tracks(self, track_ids: Union[str, int, List[Union[str, int]]]) -> List[Track]:
        """Get tracks by ID.

        Args:
            track_ids: Track ID or list of IDs.

        Returns:
            List of tracks.

        Note (RU): Получить треки по ID.
        """
        ids = self._to_id_list(track_ids)

        gql = load_query("getTracks")
        result = self._request.graphql(gql, "getTracks", {"ids": ids})
        return Track.de_list(result.get("get_tracks", []), self)

    def get_track(self, track_id: Union[str, int]) -> Optional[Track]:
        """Get a track by ID.

        Args:
            track_id: Track ID.

        Returns:
            Track or None.

        Note (RU): Получить трек по ID.
        """
        tracks = self.get_tracks(track_id)
        return tracks[0] if tracks else None

    def get_full_track(
        self,
        track_ids: Union[str, int, List[Union[str, int]]],
        with_artists: bool = False,
        with_releases: bool = False,
    ) -> List[Track]:
        """Get full track information.

        Args:
            track_ids: Track ID or list of IDs.
            with_artists: Include artist information.
            with_releases: Include release information.

        Returns:
            List of tracks with full information.

        Note (RU): Получить полную информацию о треках.
        """
        ids = self._to_id_list(track_ids)

        gql = load_query("getFullTrack")
        result = self._request.graphql(
            gql,
            "getFullTrack",
            {"ids": ids, "withArtists": with_artists, "withReleases": with_releases},
        )
        return Track.de_list(result.get("get_tracks", []), self)

    def get_stream_urls(self, track_ids: Union[str, int, List[Union[str, int]]]) -> List[Stream]:
        """Get streaming URLs.

        Args:
            track_ids: Track ID or list of IDs.

        Returns:
            List of Stream objects with URLs.

        Note (RU): Получить URL для стриминга.
        """
        ids = self._to_id_list(track_ids)

        gql = load_query("getStream")
        result = self._request.graphql(gql, "getStream", {"ids": ids})

        streams = []
        for item in result.get("media_contents", []):
            if "stream" in item:
                stream = Stream.de_json(item["stream"], self)
                if stream:
                    streams.append(stream)
        return streams

    def get_stream_url(self, track_id: Union[str, int], quality: Quality = Quality.HIGH) -> str:
        """Get streaming URL for specified quality.

        Args:
            track_id: Track ID.
            quality: Audio quality.

        Returns:
            URL for downloading/streaming.

        Raises:
            SubscriptionRequiredError: If subscription is required.
            QualityNotAvailableError: If quality is not available.

        Note (RU): Получить URL для стриминга в указанном качестве.
        """
        streams = self.get_stream_urls(track_id)
        if not streams:
            raise QualityNotAvailableError("Stream URLs not available")
        return streams[0].get_url(quality)

    # ========== Releases ==========

    def get_releases(
        self,
        release_ids: Union[str, int, List[Union[str, int]]],
        related_limit: int = 10,
    ) -> List[Release]:
        """Get releases by ID.

        Args:
            release_ids: Release ID or list of IDs.
            related_limit: Number of related releases.

        Returns:
            List of releases.

        Note (RU): Получить релизы по ID.
        """
        ids = self._to_id_list(release_ids)

        gql = load_query("getReleases")
        result = self._request.graphql(
            gql, "getReleases", {"ids": ids, "relatedLimit": related_limit}
        )
        return Release.de_list(result.get("get_releases", []), self)

    def get_release(self, release_id: Union[str, int]) -> Optional[Release]:
        """Get a release by ID.

        Args:
            release_id: Release ID.

        Returns:
            Release or None.

        Note (RU): Получить релиз по ID.
        """
        releases = self.get_releases(release_id)
        return releases[0] if releases else None

    # ========== Artists ==========

    def get_artists(
        self,
        artist_ids: Union[str, int, List[Union[str, int]]],
        with_releases: bool = False,
        releases_limit: int = 100,
        releases_offset: int = 0,
        with_popular_tracks: bool = False,
        tracks_limit: int = 100,
        tracks_offset: int = 0,
        with_related_artists: bool = False,
        related_artists_limit: int = 100,
        with_description: bool = False,
    ) -> List[Artist]:
        """Get artists by ID.

        Args:
            artist_ids: Artist ID or list of IDs.
            with_releases: Include releases.
            releases_limit: Releases limit.
            releases_offset: Releases offset.
            with_popular_tracks: Include popular tracks.
            tracks_limit: Tracks limit.
            tracks_offset: Tracks offset.
            with_related_artists: Include related artists.
            related_artists_limit: Related artists limit.
            with_description: Include description.

        Returns:
            List of artists.

        Note (RU): Получить артистов по ID.
        """
        ids = self._to_id_list(artist_ids)

        gql = load_query("getArtists")
        result = self._request.graphql(
            gql,
            "getArtists",
            {
                "ids": ids,
                "withReleases": with_releases,
                "releasesLimit": releases_limit,
                "releasesOffset": releases_offset,
                "withPopTracks": with_popular_tracks,  # Must match GraphQL
                "tracksLimit": tracks_limit,
                "tracksOffset": tracks_offset,
                "withRelatedArtists": with_related_artists,
                "releatedArtistsLimit": related_artists_limit,  # Typo in original GraphQL
                "withDescription": with_description,
            },
        )
        return Artist.de_list(result.get("get_artists", []), self)

    def get_artist(self, artist_id: Union[str, int], **kwargs: Any) -> Optional[Artist]:
        """Get an artist by ID.

        Args:
            artist_id: Artist ID.
            **kwargs: Additional parameters for get_artists.

        Returns:
            Artist or None.

        Note (RU): Получить артиста по ID.
        """
        artists = self.get_artists(artist_id, **kwargs)
        return artists[0] if artists else None

    # ========== Playlists ==========

    def get_playlists(self, playlist_ids: Union[str, int, List[Union[str, int]]]) -> List[Playlist]:
        """Get playlists by ID.

        Args:
            playlist_ids: Playlist ID or list of IDs.

        Returns:
            List of playlists.

        Note (RU): Получить плейлисты по ID.
        """
        ids = self._to_id_list(playlist_ids)

        gql = load_query("getPlaylists")
        result = self._request.graphql(gql, "getPlaylists", {"ids": ids})
        return Playlist.de_list(result.get("get_playlists", []), self)

    def get_playlist(self, playlist_id: Union[str, int]) -> Optional[Playlist]:
        """Get a playlist by ID.

        Args:
            playlist_id: Playlist ID.

        Returns:
            Playlist or None.

        Note (RU): Получить плейлист по ID.
        """
        playlists = self.get_playlists(playlist_id)
        return playlists[0] if playlists else None

    def get_short_playlist(
        self, playlist_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[SimplePlaylist]:
        """Get brief playlist information.

        Args:
            playlist_ids: Playlist ID or list of IDs.

        Returns:
            List of playlists.

        Note (RU): Получить краткую информацию о плейлистах.
        """
        ids = self._to_id_list(playlist_ids)

        gql = load_query("getShortPlaylist")
        result = self._request.graphql(gql, "getShortPlaylist", {"ids": ids})
        return SimplePlaylist.de_list(result.get("get_playlists", []), self)

    def get_playlist_tracks(
        self, playlist_id: Union[str, int], limit: int = 50, offset: int = 0
    ) -> List[SimpleTrack]:
        """Get playlist tracks with pagination.

        Args:
            playlist_id: Playlist ID.
            limit: Number of tracks.
            offset: Offset.

        Returns:
            List of tracks.

        Note (RU): Получить треки плейлиста с пагинацией.
        """
        gql = load_query("getPlaylistTracks")
        result = self._request.graphql(
            gql,
            "getPlaylistTracks",
            {"id": str(playlist_id), "limit": limit, "offset": offset},
        )
        return SimpleTrack.de_list(result.get("playlist_tracks", []), self)

    def create_playlist(self, name: str, track_ids: Optional[List[str]] = None) -> str:
        """Create a playlist.

        Args:
            name: Playlist name.
            track_ids: Track IDs to add.

        Returns:
            Created playlist ID.

        Note (RU): Создать плейлист.
        """
        gql = load_query("createPlaylist")
        items = []
        if track_ids:
            items = [{"type": "track", "item_id": tid} for tid in track_ids]

        result = self._request.graphql(gql, "createPlayList", {"name": name, "items": items})
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return str(playlist_data.get("create", ""))

    def delete_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Delete a playlist.

        Args:
            playlist_id: Playlist ID.

        Returns:
            Whether the operation succeeded.

        Note (RU): Удалить плейлист.
        """
        gql = load_query("deletePlaylist")
        result = self._request.graphql(gql, "deletePlaylist", {"id": str(playlist_id)})
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return "delete" in playlist_data

    def rename_playlist(self, playlist_id: Union[str, int], new_name: str) -> bool:
        """Rename a playlist.

        Args:
            playlist_id: Playlist ID.
            new_name: New name.

        Returns:
            Whether the operation succeeded.

        Note (RU): Переименовать плейлист.
        """
        gql = load_query("renamePlaylist")
        result = self._request.graphql(
            gql, "renamePlaylist", {"id": str(playlist_id), "name": new_name}
        )
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return "rename" in playlist_data

    def add_tracks_to_playlist(self, playlist_id: Union[str, int], track_ids: List[str]) -> bool:
        """Add tracks to a playlist.

        Args:
            playlist_id: Playlist ID.
            track_ids: Track IDs.

        Returns:
            Whether the operation succeeded.

        Note (RU): Добавить треки в плейлист.
        """
        gql = load_query("addTracksToPlaylist")
        items = [{"type": "track", "item_id": tid} for tid in track_ids]
        result = self._request.graphql(
            gql, "addTracksToPlaylist", {"id": str(playlist_id), "items": items}
        )
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return "add_items" in playlist_data

    def update_playlist(
        self,
        playlist_id: Union[str, int],
        track_ids: List[str],
        name: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> bool:
        """Update a playlist entirely.

        Args:
            playlist_id: Playlist ID.
            track_ids: New track list.
            name: New name.
            is_public: Whether public.

        Returns:
            Whether the operation succeeded.

        Note (RU): Обновить плейлист целиком.
        """
        gql = load_query("updataPlaylist")
        items = [{"type": "track", "item_id": tid} for tid in track_ids]
        variables: Dict[str, Any] = {
            "id": str(playlist_id),
            "items": items,
            "name": name or "",
            "isPublic": is_public if is_public is not None else False,
        }

        result = self._request.graphql(gql, "updataPlaylist", variables)
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return "update" in playlist_data

    def set_playlist_public(self, playlist_id: Union[str, int], is_public: bool) -> bool:
        """Change playlist visibility.

        Args:
            playlist_id: Playlist ID.
            is_public: Public or private.

        Returns:
            Whether the operation succeeded.

        Note (RU): Изменить видимость плейлиста.
        """
        gql = load_query("setPlaylistToPublic")
        result = self._request.graphql(
            gql,
            "setPlaylistToPublic",
            {"id": str(playlist_id), "isPublic": is_public},
        )
        playlist_data: Dict[str, Any] = result.get("playlist", {})
        return "set_public" in playlist_data

    def synthesis_playlist_build(
        self, first_author_id: str, second_author_id: str
    ) -> Optional[SynthesisPlaylist]:
        """Create a synthesis playlist.

        Args:
            first_author_id: First author ID.
            second_author_id: Second author ID.

        Returns:
            Synthesis playlist.

        Note (RU): Создать синтез-плейлист.
        """
        gql = load_query("synthesisPlaylistBuild")
        result = self._request.graphql(
            gql,
            "synthesisPlaylistBuild",
            {"firstAuthorId": first_author_id, "secondAuthorId": second_author_id},
        )
        return SynthesisPlaylist.de_json(result.get("synthesis_playlist_build", {}), self)

    def get_synthesis_playlists(self, ids: List[str]) -> List[SynthesisPlaylist]:
        """Get synthesis playlists.

        Args:
            ids: Playlist IDs.

        Returns:
            List of synthesis playlists.

        Note (RU): Получить синтез-плейлисты.
        """
        gql = load_query("synthesisPlaylist")
        result = self._request.graphql(gql, "synthesisPlaylist", {"ids": ids})
        return SynthesisPlaylist.de_list(result.get("synthesis_playlist", []), self)

    # ========== Podcasts ==========

    def get_podcasts(self, podcast_ids: Union[str, int, List[Union[str, int]]]) -> List[Podcast]:
        """Get podcasts by ID.

        Args:
            podcast_ids: Podcast ID or list of IDs.

        Returns:
            List of podcasts.

        Note (RU): Получить подкасты по ID.
        """
        ids = self._to_id_list(podcast_ids)

        gql = load_query("getPodcasts")
        result = self._request.graphql(gql, "getPodcasts", {"ids": ids})
        return Podcast.de_list(result.get("get_podcasts", []), self)

    def get_podcast(self, podcast_id: Union[str, int]) -> Optional[Podcast]:
        """Get a podcast by ID.

        Args:
            podcast_id: Podcast ID.

        Returns:
            Podcast or None.

        Note (RU): Получить подкаст по ID.
        """
        podcasts = self.get_podcasts(podcast_id)
        return podcasts[0] if podcasts else None

    def get_episodes(self, episode_ids: Union[str, int, List[Union[str, int]]]) -> List[Episode]:
        """Get episodes by ID.

        Args:
            episode_ids: Episode ID or list of IDs.

        Returns:
            List of episodes.

        Note (RU): Получить эпизоды по ID.
        """
        ids = self._to_id_list(episode_ids)

        gql = load_query("getEpisodes")
        result = self._request.graphql(gql, "getEpisodes", {"ids": ids})
        return Episode.de_list(result.get("get_episodes", []), self)

    def get_episode(self, episode_id: Union[str, int]) -> Optional[Episode]:
        """Get an episode by ID.

        Args:
            episode_id: Episode ID.

        Returns:
            Episode or None.

        Note (RU): Получить эпизод по ID.
        """
        episodes = self.get_episodes(episode_id)
        return episodes[0] if episodes else None

    # ========== Collection ==========

    def get_collection(self) -> Optional[Collection]:
        """Get the user's collection.

        Returns:
            Collection with likes.

        Note (RU): Получить коллекцию пользователя.
        """
        gql = load_query("userCollection")
        result = self._request.graphql(gql, "userCollection", {})
        return Collection.de_json(result.get("collection", {}), self)

    def get_liked_tracks(
        self,
        order_by: OrderBy = OrderBy.DATE_ADDED,
        direction: OrderDirection = OrderDirection.DESC,
    ) -> List[Track]:
        """Get liked tracks.

        Args:
            order_by: Sort by field.
            direction: Sort direction.

        Returns:
            List of tracks.

        Note (RU): Получить лайкнутые треки.
        """
        gql = load_query("userTracks")
        result = self._request.graphql(
            gql,
            "userTracks",
            {"orderBy": order_by.value, "orderDirection": direction.value},
        )
        collection_data: Dict[str, Any] = result.get("collection", {})
        return Track.de_list(collection_data.get("tracks", []), self)

    def get_user_playlists(self) -> List[CollectionItem]:
        """Get user's playlists.

        Returns:
            List of collection items.

        Note (RU): Получить плейлисты пользователя.
        """
        gql = load_query("userPlaylists")
        result = self._request.graphql(gql, "userPlaylists", {})
        collection_data: Dict[str, Any] = result.get("collection", {})
        return CollectionItem.de_list(collection_data.get("playlists", []), self)

    def get_user_paginated_podcasts(
        self, cursor: Optional[str] = None, count: int = 20
    ) -> Dict[str, Any]:
        """Get user's podcasts with pagination.

        Args:
            cursor: Pagination cursor.
            count: Number of podcasts.

        Returns:
            Data with podcasts and cursor.

        Note (RU): Получить подкасты пользователя с пагинацией.
        """
        gql = load_query("userPaginatedPodcasts")
        variables: Dict[str, Any] = {"count": count}
        if cursor:
            variables["cursor"] = cursor

        result = self._request.graphql(gql, "userPaginatedPodcasts", variables)
        podcasts_data: Dict[str, Any] = result.get("paginated_collection", {})
        return podcasts_data

    def add_to_collection(self, item_id: Union[str, int], item_type: CollectionItemType) -> bool:
        """Add an item to the collection (like).

        Args:
            item_id: Item ID.
            item_type: Item type.

        Returns:
            Whether the operation succeeded.

        Note (RU): Добавить элемент в коллекцию (лайк).
        """
        gql = load_query("addItemToCollection")
        result = self._request.graphql(
            gql,
            "addItemToCollection",
            {"id": str(item_id), "type": item_type.value},
        )
        collection_data: Dict[str, Any] = result.get("collection", {})
        return "add_item" in collection_data

    def remove_from_collection(
        self, item_id: Union[str, int], item_type: CollectionItemType
    ) -> bool:
        """Remove an item from the collection.

        Args:
            item_id: Item ID.
            item_type: Item type.

        Returns:
            Whether the operation succeeded.

        Note (RU): Убрать элемент из коллекции.
        """
        gql = load_query("removeItemFromCollection")
        result = self._request.graphql(
            gql,
            "removeItemFromCollection",
            {"id": str(item_id), "type": item_type.value},
        )
        collection_data: Dict[str, Any] = result.get("collection", {})
        return "remove_item" in collection_data

    # Shortcut methods for likes
    def like_track(self, track_id: Union[str, int]) -> bool:
        """Like a track.

        Note (RU): Лайкнуть трек.
        """
        return self.add_to_collection(track_id, CollectionItemType.TRACK)

    def unlike_track(self, track_id: Union[str, int]) -> bool:
        """Unlike a track.

        Note (RU): Убрать лайк с трека.
        """
        return self.remove_from_collection(track_id, CollectionItemType.TRACK)

    def like_release(self, release_id: Union[str, int]) -> bool:
        """Like a release.

        Note (RU): Лайкнуть релиз.
        """
        return self.add_to_collection(release_id, CollectionItemType.RELEASE)

    def unlike_release(self, release_id: Union[str, int]) -> bool:
        """Unlike a release.

        Note (RU): Убрать лайк с релиза.
        """
        return self.remove_from_collection(release_id, CollectionItemType.RELEASE)

    def like_artist(self, artist_id: Union[str, int]) -> bool:
        """Like an artist.

        Note (RU): Лайкнуть артиста.
        """
        return self.add_to_collection(artist_id, CollectionItemType.ARTIST)

    def unlike_artist(self, artist_id: Union[str, int]) -> bool:
        """Unlike an artist.

        Note (RU): Убрать лайк с артиста.
        """
        return self.remove_from_collection(artist_id, CollectionItemType.ARTIST)

    def like_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Like a playlist.

        Note (RU): Лайкнуть плейлист.
        """
        return self.add_to_collection(playlist_id, CollectionItemType.PLAYLIST)

    def unlike_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Unlike a playlist.

        Note (RU): Убрать лайк с плейлиста.
        """
        return self.remove_from_collection(playlist_id, CollectionItemType.PLAYLIST)

    def like_podcast(self, podcast_id: Union[str, int]) -> bool:
        """Like a podcast.

        Note (RU): Лайкнуть подкаст.
        """
        return self.add_to_collection(podcast_id, CollectionItemType.PODCAST)

    def unlike_podcast(self, podcast_id: Union[str, int]) -> bool:
        """Unlike a podcast.

        Note (RU): Убрать лайк с подкаста.
        """
        return self.remove_from_collection(podcast_id, CollectionItemType.PODCAST)

    # ========== Hidden items ==========

    def get_hidden_collection(self) -> Optional[HiddenCollection]:
        """Get hidden items.

        Returns:
            Hidden collection.

        Note (RU): Получить скрытые элементы.
        """
        gql = load_query("getAllHiddenCollection")
        result = self._request.graphql(gql, "getAllHiddenCollection", {})
        return HiddenCollection.de_json(result.get("hidden_collection", {}), self)

    def get_hidden_tracks(self) -> List[CollectionItem]:
        """Get hidden tracks.

        Returns:
            List of hidden tracks.

        Note (RU): Получить скрытые треки.
        """
        gql = load_query("getHiddenTracks")
        result = self._request.graphql(gql, "getHiddenTracks", {})
        hidden_data: Dict[str, Any] = result.get("hidden_collection", {})
        return CollectionItem.de_list(hidden_data.get("tracks", []), self)

    def add_to_hidden(self, item_id: Union[str, int], item_type: CollectionItemType) -> bool:
        """Hide an item.

        Args:
            item_id: Item ID.
            item_type: Item type.

        Returns:
            Whether the operation succeeded.

        Note (RU): Скрыть элемент.
        """
        gql = load_query("addItemToHidden")
        result = self._request.graphql(
            gql,
            "addItemToHidden",
            {"id": str(item_id), "type": item_type.value},
        )
        hidden_data: Dict[str, Any] = result.get("hidden_collection", {})
        return "add_item" in hidden_data

    def remove_from_hidden(self, item_id: Union[str, int], item_type: CollectionItemType) -> bool:
        """Remove an item from hidden.

        Args:
            item_id: Item ID.
            item_type: Item type.

        Returns:
            Whether the operation succeeded.

        Note (RU): Убрать элемент из скрытых.
        """
        gql = load_query("removeItemFromHidden")
        result = self._request.graphql(
            gql,
            "removeItemFromHidden",
            {"id": str(item_id), "type": item_type.value},
        )
        hidden_data: Dict[str, Any] = result.get("hidden_collection", {})
        return "remove_item" in hidden_data

    def hide_track(self, track_id: Union[str, int]) -> bool:
        """Hide a track.

        Note (RU): Скрыть трек.
        """
        return self.add_to_hidden(track_id, CollectionItemType.TRACK)

    def unhide_track(self, track_id: Union[str, int]) -> bool:
        """Remove a track from hidden.

        Note (RU): Убрать трек из скрытых.
        """
        return self.remove_from_hidden(track_id, CollectionItemType.TRACK)

    # ========== Profiles ==========

    def get_profile_followers_count(
        self, profile_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[int]:
        """Get profile followers count.

        Args:
            profile_ids: Profile ID or list of IDs.

        Returns:
            List of follower counts.

        Note (RU): Получить количество подписчиков профилей.
        """
        ids = self._to_id_list(profile_ids)

        gql = load_query("profileFollowersCount")
        result = self._request.graphql(gql, "profileFollowersCount", {"ids": ids})
        profiles: List[Dict[str, Any]] = result.get("profiles", [])
        return [p.get("collection_item_data", {}).get("likes_count", 0) for p in profiles]

    def get_following_count(self, profile_id: Union[str, int]) -> int:
        """Get the user's following count.

        Args:
            profile_id: Profile ID.

        Returns:
            Following count.

        Note (RU): Получить количество подписок пользователя.
        """
        gql = load_query("followingCount")
        result = self._request.graphql(gql, "followingCount", {"id": str(profile_id)})
        follows_data: Dict[str, Any] = result.get("follows", {})
        followings: Dict[str, Any] = follows_data.get("followings", {})
        count: int = followings.get("count", 0)
        return count

    # ========== History ==========

    def get_listening_history(self) -> List[Dict[str, Any]]:
        """Get listening history.

        Returns:
            Listening history.

        Note (RU): Получить историю прослушивания.
        """
        gql = load_query("listeningHistory")
        result = self._request.graphql(gql, "listeningHistory", {})
        history: List[Dict[str, Any]] = result.get("listening_history", [])
        return history

    def get_listened_episodes(self) -> List[Dict[str, Any]]:
        """Get listened episodes.

        Returns:
            Listened episodes.

        Note (RU): Получить прослушанные эпизоды.
        """
        gql = load_query("listenedEpisodes")
        result = self._request.graphql(gql, "listenedEpisodes", {})
        play_state: Dict[str, Any] = result.get("get_play_state", {})
        episodes: List[Dict[str, Any]] = play_state.get("episodes", [])
        return episodes

    def has_unread_notifications(self) -> bool:
        """Check for unread notifications.

        Returns:
            Whether there are unread notifications.

        Note (RU): Проверить наличие непрочитанных уведомлений.
        """
        gql = load_query("notificationsHasUnread")
        result = self._request.graphql(gql, "notificationsHasUnread", {})
        notification_data: Dict[str, Any] = result.get("notification", {})
        has_unread: bool = notification_data.get("has_unread", False)
        return has_unread
