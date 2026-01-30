####################################################
# THIS IS AUTO GENERATED COPY. DON'T EDIT BY HANDS #
####################################################

"""Асинхронный клиент Zvuk Music API."""

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
from zvuk_music.utils.request_async import TINY_API_URL, Request


class ClientAsync:
    """Асинхронный клиент Zvuk Music API.

    Args:
        token: Токен авторизации (получить через get_anonymous_token() или из браузера).
        timeout: Таймаут запросов в секундах.
        proxy_url: URL прокси сервера.
        user_agent: User-Agent для запросов (важно для обхода бот-защиты).
        report_unknown_fields: Логировать неизвестные поля от API.

    Example:
        >>> # Анонимный доступ (ограниченный функционал):
        >>> token = Client.get_anonymous_token()
        >>> client = Client(token=token)
        >>>
        >>> # Авторизованный доступ (полный функционал):
        >>> # 1. Войти на zvuk.com в браузере
        >>> # 2. Открыть https://zvuk.com/api/tiny/profile
        >>> # 3. Скопировать значение поля "token"
        >>> client = Client(token="ваш_токен")
    """

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
        """Получить анонимный токен.

        Анонимный токен обеспечивает ограниченный доступ:
        - Только mid качество (128kbps)
        - Нет доступа к коллекции
        - Нет возможности лайкать

        Returns:
            Анонимный токен.
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

    async def init(self) -> "ClientAsync":
        """Инициализировать клиент, загрузить профиль.

        Returns:
            self для цепочки вызовов.
        """
        await self.get_profile()
        return self

    async def get_profile(self) -> Optional[Profile]:
        """Получить профиль текущего пользователя.

        Returns:
            Профиль пользователя.
        """
        data = await self._request.get(f"{TINY_API_URL}/profile")
        # Request.get уже возвращает result, оборачиваем обратно для Profile
        profile = Profile.de_json({"result": data}, self)
        if profile and profile.result:
            self._profile = profile.result
        return profile

    async def is_authorized(self) -> bool:
        """Авторизован ли пользователь (не анонимный).

        Returns:
            True если авторизован.
        """
        if self._profile:
            return self._profile.is_authorized()
        return False

    # ========== Поиск ==========

    async def quick_search(
        self,
        query: str,
        limit: int = 10,
        search_session_id: Optional[str] = None,
    ) -> Optional[QuickSearch]:
        """Быстрый поиск с автодополнением.

        Args:
            query: Поисковый запрос.
            limit: Максимум результатов.
            search_session_id: ID сессии поиска.

        Returns:
            Результаты быстрого поиска.
        """
        gql = load_query("quickSearch")
        variables: Dict[str, Any] = {"query": query, "limit": limit}
        if search_session_id:
            variables["searchSessionId"] = search_session_id

        result = await self._request.graphql(gql, "quickSearch", variables)
        # API возвращает quick_search (snake_case после нормализации)
        data = result.get("quick_search") or result.get("quickSearch") or {}
        return QuickSearch.de_json(data, self)

    async def search(
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
        """Полнотекстовый поиск.

        Args:
            query: Поисковый запрос.
            limit: Максимум результатов в категории.
            tracks: Искать треки.
            artists: Искать артистов.
            releases: Искать релизы.
            playlists: Искать плейлисты.
            podcasts: Искать подкасты.
            episodes: Искать эпизоды.
            profiles: Искать профили.
            books: Искать книги.
            track_cursor: Курсор для треков.
            artist_cursor: Курсор для артистов.
            release_cursor: Курсор для релизов.
            playlist_cursor: Курсор для плейлистов.

        Returns:
            Результаты поиска.
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

        result = await self._request.graphql(gql, "search", variables)
        return Search.de_json(result.get("search", {}), self)

    # ========== Треки ==========

    async def get_tracks(self, track_ids: Union[str, int, List[Union[str, int]]]) -> List[Track]:
        """Получить треки по ID.

        Args:
            track_ids: ID трека или список ID.

        Returns:
            Список треков.
        """
        if not isinstance(track_ids, list):
            track_ids = [track_ids]
        ids = [str(i) for i in track_ids]

        gql = load_query("getTracks")
        result = await self._request.graphql(gql, "getTracks", {"ids": ids})
        return Track.de_list(result.get("get_tracks", []), self)

    async def get_track(self, track_id: Union[str, int]) -> Optional[Track]:
        """Получить трек по ID.

        Args:
            track_id: ID трека.

        Returns:
            Трек или None.
        """
        tracks = await self.get_tracks(track_id)
        return tracks[0] if tracks else None

    async def get_full_track(
        self,
        track_ids: Union[str, int, List[Union[str, int]]],
        with_artists: bool = False,
        with_releases: bool = False,
    ) -> List[Track]:
        """Получить полную информацию о треках.

        Args:
            track_ids: ID трека или список ID.
            with_artists: Включить информацию об артистах.
            with_releases: Включить информацию о релизах.

        Returns:
            Список треков с полной информацией.
        """
        if not isinstance(track_ids, list):
            track_ids = [track_ids]
        ids = [str(i) for i in track_ids]

        gql = load_query("getFullTrack")
        result = await self._request.graphql(
            gql,
            "getFullTrack",
            {"ids": ids, "withArtists": with_artists, "withReleases": with_releases},
        )
        return Track.de_list(result.get("get_tracks", []), self)

    async def get_stream_urls(
        self, track_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[Stream]:
        """Получить URL для стриминга.

        Args:
            track_ids: ID трека или список ID.

        Returns:
            Список объектов Stream с URL.
        """
        if not isinstance(track_ids, list):
            track_ids = [track_ids]
        ids = [str(i) for i in track_ids]

        gql = load_query("getStream")
        result = await self._request.graphql(gql, "getStream", {"ids": ids})

        streams = []
        for item in result.get("media_contents", []):
            if "stream" in item:
                stream = Stream.de_json(item["stream"], self)
                if stream:
                    streams.append(stream)
        return streams

    async def get_stream_url(
        self, track_id: Union[str, int], quality: Quality = Quality.HIGH
    ) -> str:
        """Получить URL для стриминга в указанном качестве.

        Args:
            track_id: ID трека.
            quality: Качество аудио.

        Returns:
            URL для скачивания/стриминга.

        Raises:
            SubscriptionRequiredError: Если требуется подписка.
            QualityNotAvailableError: Если качество недоступно.
        """
        streams = await self.get_stream_urls(track_id)
        if not streams:
            raise QualityNotAvailableError("Stream URLs not available")
        return streams[0].get_url(quality)

    # ========== Релизы ==========

    async def get_releases(
        self,
        release_ids: Union[str, int, List[Union[str, int]]],
        related_limit: int = 10,
    ) -> List[Release]:
        """Получить релизы по ID.

        Args:
            release_ids: ID релиза или список ID.
            related_limit: Количество похожих релизов.

        Returns:
            Список релизов.
        """
        if not isinstance(release_ids, list):
            release_ids = [release_ids]
        ids = [str(i) for i in release_ids]

        gql = load_query("getReleases")
        result = await self._request.graphql(
            gql, "getReleases", {"ids": ids, "relatedLimit": related_limit}
        )
        return Release.de_list(result.get("get_releases", []), self)

    async def get_release(self, release_id: Union[str, int]) -> Optional[Release]:
        """Получить релиз по ID.

        Args:
            release_id: ID релиза.

        Returns:
            Релиз или None.
        """
        releases = await self.get_releases(release_id)
        return releases[0] if releases else None

    # ========== Артисты ==========

    async def get_artists(
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
        """Получить артистов по ID.

        Args:
            artist_ids: ID артиста или список ID.
            with_releases: Включить релизы.
            releases_limit: Лимит релизов.
            releases_offset: Смещение релизов.
            with_popular_tracks: Включить популярные треки.
            tracks_limit: Лимит треков.
            tracks_offset: Смещение треков.
            with_related_artists: Включить похожих артистов.
            related_artists_limit: Лимит похожих артистов.
            with_description: Включить описание.

        Returns:
            Список артистов.
        """
        if not isinstance(artist_ids, list):
            artist_ids = [artist_ids]
        ids = [str(i) for i in artist_ids]

        gql = load_query("getArtists")
        result = await self._request.graphql(
            gql,
            "getArtists",
            {
                "ids": ids,
                "withReleases": with_releases,
                "releasesLimit": releases_limit,
                "releasesOffset": releases_offset,
                "withPopTracks": with_popular_tracks,  # Должно соответствовать GraphQL
                "tracksLimit": tracks_limit,
                "tracksOffset": tracks_offset,
                "withRelatedArtists": with_related_artists,
                "releatedArtistsLimit": related_artists_limit,  # Опечатка в оригинальном GraphQL
                "withDescription": with_description,
            },
        )
        return Artist.de_list(result.get("get_artists", []), self)

    async def get_artist(self, artist_id: Union[str, int], **kwargs: Any) -> Optional[Artist]:
        """Получить артиста по ID.

        Args:
            artist_id: ID артиста.
            **kwargs: Дополнительные параметры для get_artists.

        Returns:
            Артист или None.
        """
        artists = await self.get_artists(artist_id, **kwargs)
        return artists[0] if artists else None

    # ========== Плейлисты ==========

    async def get_playlists(
        self, playlist_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[Playlist]:
        """Получить плейлисты по ID.

        Args:
            playlist_ids: ID плейлиста или список ID.

        Returns:
            Список плейлистов.
        """
        if not isinstance(playlist_ids, list):
            playlist_ids = [playlist_ids]
        ids = [str(i) for i in playlist_ids]

        gql = load_query("getPlaylists")
        result = await self._request.graphql(gql, "getPlaylists", {"ids": ids})
        return Playlist.de_list(result.get("get_playlists", []), self)

    async def get_playlist(self, playlist_id: Union[str, int]) -> Optional[Playlist]:
        """Получить плейлист по ID.

        Args:
            playlist_id: ID плейлиста.

        Returns:
            Плейлист или None.
        """
        playlists = await self.get_playlists(playlist_id)
        return playlists[0] if playlists else None

    async def get_short_playlist(
        self, playlist_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[SimplePlaylist]:
        """Получить краткую информацию о плейлистах.

        Args:
            playlist_ids: ID плейлиста или список ID.

        Returns:
            Список плейлистов.
        """
        if not isinstance(playlist_ids, list):
            playlist_ids = [playlist_ids]
        ids = [str(i) for i in playlist_ids]

        gql = load_query("getShortPlaylist")
        result = await self._request.graphql(gql, "getShortPlaylist", {"ids": ids})
        return SimplePlaylist.de_list(result.get("get_playlists", []), self)

    async def get_playlist_tracks(
        self, playlist_id: Union[str, int], limit: int = 50, offset: int = 0
    ) -> List[SimpleTrack]:
        """Получить треки плейлиста с пагинацией.

        Args:
            playlist_id: ID плейлиста.
            limit: Количество треков.
            offset: Смещение.

        Returns:
            Список треков.
        """
        gql = load_query("getPlaylistTracks")
        result = await self._request.graphql(
            gql,
            "getPlaylistTracks",
            {"id": str(playlist_id), "limit": limit, "offset": offset},
        )
        return SimpleTrack.de_list(result.get("playlist_tracks", []), self)

    async def create_playlist(self, name: str, track_ids: Optional[List[str]] = None) -> str:
        """Создать плейлист.

        Args:
            name: Название плейлиста.
            track_ids: ID треков для добавления.

        Returns:
            ID созданного плейлиста.
        """
        gql = load_query("createPlaylist")
        items = []
        if track_ids:
            items = [{"type": "track", "itemId": tid} for tid in track_ids]

        result = await self._request.graphql(gql, "createPlaylist", {"name": name, "items": items})
        create_data: Dict[str, Any] = result.get("playlist_create", {})
        return str(create_data.get("id", ""))

    async def delete_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Удалить плейлист.

        Args:
            playlist_id: ID плейлиста.

        Returns:
            Успешность операции.
        """
        gql = load_query("deletePlaylist")
        result = await self._request.graphql(
            gql, "deletePlaylist", {"playlistId": str(playlist_id)}
        )
        return result.get("playlist_delete") is True

    async def rename_playlist(self, playlist_id: Union[str, int], new_name: str) -> bool:
        """Переименовать плейлист.

        Args:
            playlist_id: ID плейлиста.
            new_name: Новое название.

        Returns:
            Успешность операции.
        """
        gql = load_query("renamePlaylist")
        result = await self._request.graphql(
            gql, "renamePlaylist", {"playlistId": str(playlist_id), "name": new_name}
        )
        return result.get("playlist_rename") is not None

    async def add_tracks_to_playlist(
        self, playlist_id: Union[str, int], track_ids: List[str]
    ) -> bool:
        """Добавить треки в плейлист.

        Args:
            playlist_id: ID плейлиста.
            track_ids: ID треков.

        Returns:
            Успешность операции.
        """
        gql = load_query("addTracksToPlaylist")
        items = [{"type": "track", "itemId": tid} for tid in track_ids]
        result = await self._request.graphql(
            gql, "addTracksToPlaylist", {"playlistId": str(playlist_id), "items": items}
        )
        return result.get("playlist_add_items") is not None

    async def update_playlist(
        self,
        playlist_id: Union[str, int],
        track_ids: List[str],
        name: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> bool:
        """Обновить плейлист целиком.

        Args:
            playlist_id: ID плейлиста.
            track_ids: Новый список треков.
            name: Новое название.
            is_public: Публичный ли.

        Returns:
            Успешность операции.
        """
        gql = load_query("updataPlaylist")
        items = [{"type": "track", "itemId": tid} for tid in track_ids]
        variables: Dict[str, Any] = {
            "playlistId": str(playlist_id),
            "items": items,
        }
        if name is not None:
            variables["name"] = name
        if is_public is not None:
            variables["isPublic"] = is_public

        result = await self._request.graphql(gql, "updatePlaylist", variables)
        return result.get("playlist_update") is not None

    async def set_playlist_public(self, playlist_id: Union[str, int], is_public: bool) -> bool:
        """Изменить видимость плейлиста.

        Args:
            playlist_id: ID плейлиста.
            is_public: Публичный или приватный.

        Returns:
            Успешность операции.
        """
        gql = load_query("setPlaylistToPublic")
        result = await self._request.graphql(
            gql,
            "setPlaylistToPublic",
            {"playlistId": str(playlist_id), "isPublic": is_public},
        )
        return result.get("playlist_set_is_public") is not None

    async def synthesis_playlist_build(
        self, first_author_id: str, second_author_id: str
    ) -> Optional[SynthesisPlaylist]:
        """Создать синтез-плейлист.

        Args:
            first_author_id: ID первого автора.
            second_author_id: ID второго автора.

        Returns:
            Синтез-плейлист.
        """
        gql = load_query("synthesisPlaylistBuild")
        result = await self._request.graphql(
            gql,
            "synthesisPlaylistBuild",
            {"firstAuthorId": first_author_id, "secondAuthorId": second_author_id},
        )
        return SynthesisPlaylist.de_json(result.get("synthesis_playlist_build", {}), self)

    async def get_synthesis_playlists(self, ids: List[str]) -> List[SynthesisPlaylist]:
        """Получить синтез-плейлисты.

        Args:
            ids: ID плейлистов.

        Returns:
            Список синтез-плейлистов.
        """
        gql = load_query("synthesisPlaylist")
        result = await self._request.graphql(gql, "synthesisPlaylist", {"ids": ids})
        return SynthesisPlaylist.de_list(result.get("synthesis_playlist", []), self)

    # ========== Подкасты ==========

    async def get_podcasts(
        self, podcast_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[Podcast]:
        """Получить подкасты по ID.

        Args:
            podcast_ids: ID подкаста или список ID.

        Returns:
            Список подкастов.
        """
        if not isinstance(podcast_ids, list):
            podcast_ids = [podcast_ids]
        ids = [str(i) for i in podcast_ids]

        gql = load_query("getPodcasts")
        result = await self._request.graphql(gql, "getPodcasts", {"ids": ids})
        return Podcast.de_list(result.get("get_podcasts", []), self)

    async def get_podcast(self, podcast_id: Union[str, int]) -> Optional[Podcast]:
        """Получить подкаст по ID.

        Args:
            podcast_id: ID подкаста.

        Returns:
            Подкаст или None.
        """
        podcasts = await self.get_podcasts(podcast_id)
        return podcasts[0] if podcasts else None

    async def get_episodes(
        self, episode_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[Episode]:
        """Получить эпизоды по ID.

        Args:
            episode_ids: ID эпизода или список ID.

        Returns:
            Список эпизодов.
        """
        if not isinstance(episode_ids, list):
            episode_ids = [episode_ids]
        ids = [str(i) for i in episode_ids]

        gql = load_query("getEpisodes")
        result = await self._request.graphql(gql, "getEpisodes", {"ids": ids})
        return Episode.de_list(result.get("get_episodes", []), self)

    async def get_episode(self, episode_id: Union[str, int]) -> Optional[Episode]:
        """Получить эпизод по ID.

        Args:
            episode_id: ID эпизода.

        Returns:
            Эпизод или None.
        """
        episodes = await self.get_episodes(episode_id)
        return episodes[0] if episodes else None

    # ========== Коллекция ==========

    async def get_collection(self) -> Optional[Collection]:
        """Получить коллекцию пользователя.

        Returns:
            Коллекция с лайками.
        """
        gql = load_query("userCollection")
        result = await self._request.graphql(gql, "userCollection", {})
        return Collection.de_json(result.get("collection", {}), self)

    async def get_liked_tracks(
        self,
        order_by: OrderBy = OrderBy.DATE_ADDED,
        direction: OrderDirection = OrderDirection.DESC,
    ) -> List[Track]:
        """Получить лайкнутые треки.

        Args:
            order_by: Сортировка по полю.
            direction: Направление сортировки.

        Returns:
            Список треков.
        """
        gql = load_query("userTracks")
        result = await self._request.graphql(
            gql,
            "userTracks",
            {"orderBy": order_by.value, "orderDirection": direction.value},
        )
        collection_data: Dict[str, Any] = result.get("collection", {})
        return Track.de_list(collection_data.get("tracks", []), self)

    async def get_user_playlists(self) -> List[CollectionItem]:
        """Получить плейлисты пользователя.

        Returns:
            Список элементов коллекции.
        """
        gql = load_query("userPlaylists")
        result = await self._request.graphql(gql, "userPlaylists", {})
        collection_data: Dict[str, Any] = result.get("collection", {})
        return CollectionItem.de_list(collection_data.get("playlists", []), self)

    async def get_user_paginated_podcasts(
        self, cursor: Optional[str] = None, count: int = 20
    ) -> Dict[str, Any]:
        """Получить подкасты пользователя с пагинацией.

        Args:
            cursor: Курсор для пагинации.
            count: Количество подкастов.

        Returns:
            Данные с подкастами и курсором.
        """
        gql = load_query("userPaginatedPodcasts")
        variables: Dict[str, Any] = {"count": count}
        if cursor:
            variables["cursor"] = cursor

        result = await self._request.graphql(gql, "userPaginatedPodcasts", variables)
        podcasts_data: Dict[str, Any] = result.get("paginated_collection", {})
        return podcasts_data

    async def add_to_collection(
        self, item_id: Union[str, int], item_type: CollectionItemType
    ) -> bool:
        """Добавить элемент в коллекцию (лайк).

        Args:
            item_id: ID элемента.
            item_type: Тип элемента.

        Returns:
            Успешность операции.
        """
        gql = load_query("addItemToCollection")
        result = await self._request.graphql(
            gql,
            "addItemToCollection",
            {"itemId": str(item_id), "itemType": item_type.value},
        )
        return result.get("collection_add_item") is not None

    async def remove_from_collection(
        self, item_id: Union[str, int], item_type: CollectionItemType
    ) -> bool:
        """Убрать элемент из коллекции.

        Args:
            item_id: ID элемента.
            item_type: Тип элемента.

        Returns:
            Успешность операции.
        """
        gql = load_query("removeItemFromCollection")
        result = await self._request.graphql(
            gql,
            "removeItemFromCollection",
            {"itemId": str(item_id), "itemType": item_type.value},
        )
        return result.get("collection_remove_item") is not None

    # Shortcut методы для лайков
    async def like_track(self, track_id: Union[str, int]) -> bool:
        """Лайкнуть трек."""
        return await self.add_to_collection(track_id, CollectionItemType.TRACK)

    async def unlike_track(self, track_id: Union[str, int]) -> bool:
        """Убрать лайк с трека."""
        return await self.remove_from_collection(track_id, CollectionItemType.TRACK)

    async def like_release(self, release_id: Union[str, int]) -> bool:
        """Лайкнуть релиз."""
        return await self.add_to_collection(release_id, CollectionItemType.RELEASE)

    async def unlike_release(self, release_id: Union[str, int]) -> bool:
        """Убрать лайк с релиза."""
        return await self.remove_from_collection(release_id, CollectionItemType.RELEASE)

    async def like_artist(self, artist_id: Union[str, int]) -> bool:
        """Лайкнуть артиста."""
        return await self.add_to_collection(artist_id, CollectionItemType.ARTIST)

    async def unlike_artist(self, artist_id: Union[str, int]) -> bool:
        """Убрать лайк с артиста."""
        return await self.remove_from_collection(artist_id, CollectionItemType.ARTIST)

    async def like_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Лайкнуть плейлист."""
        return await self.add_to_collection(playlist_id, CollectionItemType.PLAYLIST)

    async def unlike_playlist(self, playlist_id: Union[str, int]) -> bool:
        """Убрать лайк с плейлиста."""
        return await self.remove_from_collection(playlist_id, CollectionItemType.PLAYLIST)

    async def like_podcast(self, podcast_id: Union[str, int]) -> bool:
        """Лайкнуть подкаст."""
        return await self.add_to_collection(podcast_id, CollectionItemType.PODCAST)

    async def unlike_podcast(self, podcast_id: Union[str, int]) -> bool:
        """Убрать лайк с подкаста."""
        return await self.remove_from_collection(podcast_id, CollectionItemType.PODCAST)

    # ========== Скрытые элементы ==========

    async def get_hidden_collection(self) -> Optional[HiddenCollection]:
        """Получить скрытые элементы.

        Returns:
            Скрытая коллекция.
        """
        gql = load_query("getAllHiddenCollection")
        result = await self._request.graphql(gql, "getAllHiddenCollection", {})
        return HiddenCollection.de_json(result.get("hidden_collection", {}), self)

    async def get_hidden_tracks(self) -> List[CollectionItem]:
        """Получить скрытые треки.

        Returns:
            Список скрытых треков.
        """
        gql = load_query("getHiddenTracks")
        result = await self._request.graphql(gql, "getHiddenTracks", {})
        hidden_data: Dict[str, Any] = result.get("hidden_collection", {})
        return CollectionItem.de_list(hidden_data.get("tracks", []), self)

    async def add_to_hidden(self, item_id: Union[str, int], item_type: CollectionItemType) -> bool:
        """Скрыть элемент.

        Args:
            item_id: ID элемента.
            item_type: Тип элемента.

        Returns:
            Успешность операции.
        """
        gql = load_query("addItemToHidden")
        result = await self._request.graphql(
            gql,
            "addItemToHidden",
            {"itemId": str(item_id), "itemType": item_type.value},
        )
        return result.get("hidden_add_item") is not None

    async def remove_from_hidden(
        self, item_id: Union[str, int], item_type: CollectionItemType
    ) -> bool:
        """Убрать элемент из скрытых.

        Args:
            item_id: ID элемента.
            item_type: Тип элемента.

        Returns:
            Успешность операции.
        """
        gql = load_query("removeItemFromHidden")
        result = await self._request.graphql(
            gql,
            "removeItemFromHidden",
            {"itemId": str(item_id), "itemType": item_type.value},
        )
        return result.get("hidden_remove_item") is not None

    async def hide_track(self, track_id: Union[str, int]) -> bool:
        """Скрыть трек."""
        return await self.add_to_hidden(track_id, CollectionItemType.TRACK)

    async def unhide_track(self, track_id: Union[str, int]) -> bool:
        """Убрать трек из скрытых."""
        return await self.remove_from_hidden(track_id, CollectionItemType.TRACK)

    # ========== Профили ==========

    async def get_profile_followers_count(
        self, profile_ids: Union[str, int, List[Union[str, int]]]
    ) -> List[int]:
        """Получить количество подписчиков профилей.

        Args:
            profile_ids: ID профиля или список ID.

        Returns:
            Список количества подписчиков.
        """
        if not isinstance(profile_ids, list):
            profile_ids = [profile_ids]
        ids = [str(i) for i in profile_ids]

        gql = load_query("profileFollowersCount")
        result = await self._request.graphql(gql, "profileFollowersCount", {"ids": ids})
        profiles: List[Dict[str, Any]] = result.get("profiles", [])
        return [p.get("followers_count", 0) for p in profiles]

    async def get_following_count(self, profile_id: Union[str, int]) -> int:
        """Получить количество подписок пользователя.

        Args:
            profile_id: ID профиля.

        Returns:
            Количество подписок.
        """
        gql = load_query("followingCount")
        result = await self._request.graphql(gql, "followingCount", {"id": str(profile_id)})
        follows_data: Dict[str, Any] = result.get("follows", {})
        followings: Dict[str, Any] = follows_data.get("followings", {})
        count: int = followings.get("count", 0)
        return count

    # ========== История ==========

    async def get_listening_history(self) -> List[Dict[str, Any]]:
        """Получить историю прослушивания.

        Returns:
            История прослушивания.
        """
        gql = load_query("listeningHistory")
        result = await self._request.graphql(gql, "listeningHistory", {})
        history: List[Dict[str, Any]] = result.get("listening_history", [])
        return history

    async def get_listened_episodes(self) -> List[Dict[str, Any]]:
        """Получить прослушанные эпизоды.

        Returns:
            Прослушанные эпизоды.
        """
        gql = load_query("listenedEpisodes")
        result = await self._request.graphql(gql, "listenedEpisodes", {})
        episodes: List[Dict[str, Any]] = result.get("listened_episodes", [])
        return episodes

    async def has_unread_notifications(self) -> bool:
        """Проверить наличие непрочитанных уведомлений.

        Returns:
            Есть ли непрочитанные уведомления.
        """
        gql = load_query("notificationsHasUnread")
        result = await self._request.graphql(gql, "notificationsHasUnread", {})
        notification_data: Dict[str, Any] = result.get("notification", {})
        has_unread: bool = notification_data.get("has_unread", False)
        return has_unread
