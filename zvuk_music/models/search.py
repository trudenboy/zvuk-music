"""Модели поиска."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.artist import SimpleArtist
from zvuk_music.models.book import SimpleBook
from zvuk_music.models.playlist import SimplePlaylist
from zvuk_music.models.podcast import SimpleEpisode, SimplePodcast
from zvuk_music.models.profile import SimpleProfile
from zvuk_music.models.release import SimpleRelease
from zvuk_music.models.track import SimpleTrack
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


# Type alias для cursor-based пагинации
Cursor = str

T = TypeVar("T")


@model
class Page(ZvukMusicModel):
    """Информация о пагинации.

    Attributes:
        total: Общее количество.
        prev: Предыдущая страница.
        next: Следующая страница.
        cursor: Курсор для следующей страницы.
    """

    client: Optional["ClientType"] = None
    total: Optional[int] = None
    prev: Optional[int] = None
    next: Optional[int] = None
    cursor: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.total, self.cursor)

    def has_next(self) -> bool:
        """Есть ли следующая страница."""
        return self.next is not None or self.cursor is not None

    def has_prev(self) -> bool:
        """Есть ли предыдущая страница."""
        return self.prev is not None


@model
class SearchResult(ZvukMusicModel, Generic[T]):
    """Результат поиска.

    Attributes:
        page: Информация о пагинации.
        score: Релевантность.
        items: Найденные элементы.
    """

    client: Optional["ClientType"] = None
    page: Optional[Page] = None
    score: float = 0.0
    items: List[T] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = []

    @classmethod
    def de_json_with_type(
        cls, data: JSONType, client: "ClientType", item_class: type
    ) -> Optional[Self]:
        """Десериализация с указанием типа элементов."""
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "page" in data:
            data["page"] = Page.de_json(data["page"], client)
        if "items" in data:
            data["items"] = item_class.de_list(data["items"], client)

        return cls(client=client, **cls.cleanup_data(data, client))


@model
class Search(ZvukMusicModel):
    """Результаты поиска.

    Attributes:
        search_id: ID поисковой сессии.
        tracks: Найденные треки.
        artists: Найденные артисты.
        releases: Найденные релизы.
        playlists: Найденные плейлисты.
        profiles: Найденные профили.
        books: Найденные книги.
        episodes: Найденные эпизоды.
        podcasts: Найденные подкасты.
    """

    client: Optional["ClientType"] = None
    search_id: str = ""
    tracks: Optional[SearchResult[SimpleTrack]] = None
    artists: Optional[SearchResult[SimpleArtist]] = None
    releases: Optional[SearchResult[SimpleRelease]] = None
    playlists: Optional[SearchResult[SimplePlaylist]] = None
    profiles: Optional[SearchResult[SimpleProfile]] = None
    books: Optional[SearchResult[SimpleBook]] = None
    episodes: Optional[SearchResult[SimpleEpisode]] = None
    podcasts: Optional[SearchResult[SimplePodcast]] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.search_id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "tracks" in data and data["tracks"]:
            data["tracks"] = SearchResult.de_json_with_type(data["tracks"], client, SimpleTrack)
        if "artists" in data and data["artists"]:
            data["artists"] = SearchResult.de_json_with_type(data["artists"], client, SimpleArtist)
        if "releases" in data and data["releases"]:
            data["releases"] = SearchResult.de_json_with_type(
                data["releases"], client, SimpleRelease
            )
        if "playlists" in data and data["playlists"]:
            data["playlists"] = SearchResult.de_json_with_type(
                data["playlists"], client, SimplePlaylist
            )
        if "profiles" in data and data["profiles"]:
            data["profiles"] = SearchResult.de_json_with_type(
                data["profiles"], client, SimpleProfile
            )
        if "books" in data and data["books"]:
            data["books"] = SearchResult.de_json_with_type(data["books"], client, SimpleBook)
        if "episodes" in data and data["episodes"]:
            data["episodes"] = SearchResult.de_json_with_type(
                data["episodes"], client, SimpleEpisode
            )
        if "podcasts" in data and data["podcasts"]:
            data["podcasts"] = SearchResult.de_json_with_type(
                data["podcasts"], client, SimplePodcast
            )

        return cls(client=client, **cls.cleanup_data(data, client))


@model
class QuickSearch(ZvukMusicModel):
    """Результаты быстрого поиска.

    API возвращает массив `content` со смешанными типами,
    которые разделяются по полю `__typename`.

    Attributes:
        search_session_id: ID поисковой сессии.
        tracks: Найденные треки.
        artists: Найденные артисты.
        releases: Найденные релизы.
        playlists: Найденные плейлисты.
        profiles: Найденные профили.
        books: Найденные книги.
        episodes: Найденные эпизоды.
        podcasts: Найденные подкасты.
    """

    client: Optional["ClientType"] = None
    search_session_id: str = ""
    tracks: List[SimpleTrack] = None  # type: ignore[assignment]
    artists: List[SimpleArtist] = None  # type: ignore[assignment]
    releases: List[SimpleRelease] = None  # type: ignore[assignment]
    playlists: List[SimplePlaylist] = None  # type: ignore[assignment]
    profiles: List[SimpleProfile] = None  # type: ignore[assignment]
    books: List[SimpleBook] = None  # type: ignore[assignment]
    episodes: List[SimpleEpisode] = None  # type: ignore[assignment]
    podcasts: List[SimplePodcast] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._id_attrs = (self.search_session_id,)
        if self.tracks is None:
            self.tracks = []
        if self.artists is None:
            self.artists = []
        if self.releases is None:
            self.releases = []
        if self.playlists is None:
            self.playlists = []
        if self.profiles is None:
            self.profiles = []
        if self.books is None:
            self.books = []
        if self.episodes is None:
            self.episodes = []
        if self.podcasts is None:
            self.podcasts = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        # API возвращает content как смешанный массив с __typename
        if "content" in data and isinstance(data["content"], list):
            tracks_data = []
            artists_data = []
            releases_data = []
            playlists_data = []
            profiles_data = []
            books_data = []
            episodes_data = []
            podcasts_data = []

            for item in data["content"]:
                if not isinstance(item, dict):
                    continue
                typename = item.get("__typename", "")
                if typename == "Track":
                    tracks_data.append(item)
                elif typename == "Artist":
                    artists_data.append(item)
                elif typename == "Release":
                    releases_data.append(item)
                elif typename == "Playlist":
                    playlists_data.append(item)
                elif typename == "Profile":
                    profiles_data.append(item)
                elif typename == "Book":
                    books_data.append(item)
                elif typename == "Episode":
                    episodes_data.append(item)
                elif typename == "Podcast":
                    podcasts_data.append(item)

            data["tracks"] = SimpleTrack.de_list(tracks_data, client)
            data["artists"] = SimpleArtist.de_list(artists_data, client)
            data["releases"] = SimpleRelease.de_list(releases_data, client)
            data["playlists"] = SimplePlaylist.de_list(playlists_data, client)
            data["profiles"] = SimpleProfile.de_list(profiles_data, client)
            data["books"] = SimpleBook.de_list(books_data, client)
            data["episodes"] = SimpleEpisode.de_list(episodes_data, client)
            data["podcasts"] = SimplePodcast.de_list(podcasts_data, client)
            del data["content"]
        else:
            # Fallback для старого формата (отдельные списки)
            if "tracks" in data:
                data["tracks"] = SimpleTrack.de_list(data["tracks"], client)
            if "artists" in data:
                data["artists"] = SimpleArtist.de_list(data["artists"], client)
            if "releases" in data:
                data["releases"] = SimpleRelease.de_list(data["releases"], client)
            if "playlists" in data:
                data["playlists"] = SimplePlaylist.de_list(data["playlists"], client)
            if "profiles" in data:
                data["profiles"] = SimpleProfile.de_list(data["profiles"], client)
            if "books" in data:
                data["books"] = SimpleBook.de_list(data["books"], client)
            if "episodes" in data:
                data["episodes"] = SimpleEpisode.de_list(data["episodes"], client)
            if "podcasts" in data:
                data["podcasts"] = SimplePodcast.de_list(data["podcasts"], client)

        return cls(client=client, **cls.cleanup_data(data, client))
