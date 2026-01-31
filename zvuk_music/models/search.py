"""Search models.

Note (RU): Модели поиска.
"""

from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, TypeVar

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


# Type alias for cursor-based pagination
Cursor = str

T = TypeVar("T")


@model
class Page(ZvukMusicModel):
    """Pagination information.

    Attributes:
        total: Total count.
        prev: Previous page.
        next: Next page.
        cursor: Cursor for the next page.

    Note (RU): Информация о пагинации.
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
        """Check if there is a next page.

        Note (RU): Есть ли следующая страница.
        """
        return self.next is not None or self.cursor is not None

    def has_prev(self) -> bool:
        """Check if there is a previous page.

        Note (RU): Есть ли предыдущая страница.
        """
        return self.prev is not None


@model
class SearchResult(ZvukMusicModel, Generic[T]):
    """Search result.

    Attributes:
        page: Pagination information.
        score: Relevance.
        items: Found items.

    Note (RU): Результат поиска.
        page: Информация о пагинации.
        score: Релевантность.
        items: Найденные элементы.
    """

    client: Optional["ClientType"] = None
    page: Optional[Page] = None
    score: float = 0.0
    items: List[T] = field(default_factory=list)

    @classmethod
    def de_json_with_type(
        cls, data: JSONType, client: "ClientType", item_class: type[ZvukMusicModel]
    ) -> Optional[Self]:
        """Deserialize with specified item type.

        Note (RU): Десериализация с указанием типа элементов.
        """
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "page" in data_dict:
            data_dict["page"] = Page.de_json(data_dict["page"], client)
        if "items" in data_dict:
            data_dict["items"] = item_class.de_list(data_dict["items"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))


@model
class Search(ZvukMusicModel):
    """Search results.

    Attributes:
        search_id: Search session ID.
        tracks: Found tracks.
        artists: Found artists.
        releases: Found releases.
        playlists: Found playlists.
        profiles: Found profiles.
        books: Found books.
        episodes: Found episodes.
        podcasts: Found podcasts.

    Note (RU): Результаты поиска.
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

        data_dict: Dict[str, Any] = data.copy()

        if "tracks" in data_dict and data_dict["tracks"]:
            data_dict["tracks"] = SearchResult.de_json_with_type(
                data_dict["tracks"], client, SimpleTrack
            )
        if "artists" in data_dict and data_dict["artists"]:
            data_dict["artists"] = SearchResult.de_json_with_type(
                data_dict["artists"], client, SimpleArtist
            )
        if "releases" in data_dict and data_dict["releases"]:
            data_dict["releases"] = SearchResult.de_json_with_type(
                data_dict["releases"], client, SimpleRelease
            )
        if "playlists" in data_dict and data_dict["playlists"]:
            data_dict["playlists"] = SearchResult.de_json_with_type(
                data_dict["playlists"], client, SimplePlaylist
            )
        if "profiles" in data_dict and data_dict["profiles"]:
            data_dict["profiles"] = SearchResult.de_json_with_type(
                data_dict["profiles"], client, SimpleProfile
            )
        if "books" in data_dict and data_dict["books"]:
            data_dict["books"] = SearchResult.de_json_with_type(
                data_dict["books"], client, SimpleBook
            )
        if "episodes" in data_dict and data_dict["episodes"]:
            data_dict["episodes"] = SearchResult.de_json_with_type(
                data_dict["episodes"], client, SimpleEpisode
            )
        if "podcasts" in data_dict and data_dict["podcasts"]:
            data_dict["podcasts"] = SearchResult.de_json_with_type(
                data_dict["podcasts"], client, SimplePodcast
            )

        return cls(client=client, **cls.cleanup_data(data_dict, client))


@model
class QuickSearch(ZvukMusicModel):
    """Quick search results.

    The API returns a `content` array with mixed types,
    which are separated by the `__typename` field.

    Attributes:
        search_session_id: Search session ID.
        tracks: Found tracks.
        artists: Found artists.
        releases: Found releases.
        playlists: Found playlists.
        profiles: Found profiles.
        books: Found books.
        episodes: Found episodes.
        podcasts: Found podcasts.

    Note (RU): Результаты быстрого поиска.
        API возвращает массив `content` со смешанными типами,
        которые разделяются по полю `__typename`.
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
    tracks: List[SimpleTrack] = field(default_factory=list)
    artists: List[SimpleArtist] = field(default_factory=list)
    releases: List[SimpleRelease] = field(default_factory=list)
    playlists: List[SimplePlaylist] = field(default_factory=list)
    profiles: List[SimpleProfile] = field(default_factory=list)
    books: List[SimpleBook] = field(default_factory=list)
    episodes: List[SimpleEpisode] = field(default_factory=list)
    podcasts: List[SimplePodcast] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.search_session_id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        # API returns content as a mixed array with __typename
        if "content" in data_dict and isinstance(data_dict["content"], list):
            tracks_data = []
            artists_data = []
            releases_data = []
            playlists_data = []
            profiles_data = []
            books_data = []
            episodes_data = []
            podcasts_data = []

            for item in data_dict["content"]:
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

            data_dict["tracks"] = SimpleTrack.de_list(tracks_data, client)
            data_dict["artists"] = SimpleArtist.de_list(artists_data, client)
            data_dict["releases"] = SimpleRelease.de_list(releases_data, client)
            data_dict["playlists"] = SimplePlaylist.de_list(playlists_data, client)
            data_dict["profiles"] = SimpleProfile.de_list(profiles_data, client)
            data_dict["books"] = SimpleBook.de_list(books_data, client)
            data_dict["episodes"] = SimpleEpisode.de_list(episodes_data, client)
            data_dict["podcasts"] = SimplePodcast.de_list(podcasts_data, client)
            del data_dict["content"]
        else:
            # Fallback for legacy format (separate lists)
            if "tracks" in data_dict:
                data_dict["tracks"] = SimpleTrack.de_list(data_dict["tracks"], client)
            if "artists" in data_dict:
                data_dict["artists"] = SimpleArtist.de_list(data_dict["artists"], client)
            if "releases" in data_dict:
                data_dict["releases"] = SimpleRelease.de_list(data_dict["releases"], client)
            if "playlists" in data_dict:
                data_dict["playlists"] = SimplePlaylist.de_list(data_dict["playlists"], client)
            if "profiles" in data_dict:
                data_dict["profiles"] = SimpleProfile.de_list(data_dict["profiles"], client)
            if "books" in data_dict:
                data_dict["books"] = SimpleBook.de_list(data_dict["books"], client)
            if "episodes" in data_dict:
                data_dict["episodes"] = SimpleEpisode.de_list(data_dict["episodes"], client)
            if "podcasts" in data_dict:
                data_dict["podcasts"] = SimplePodcast.de_list(data_dict["podcasts"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))
