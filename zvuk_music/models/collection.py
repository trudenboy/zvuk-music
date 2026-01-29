"""Модели коллекции (лайки, скрытые)."""

from typing import TYPE_CHECKING, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.enums import CollectionItemStatus
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class CollectionItem(ZvukMusicModel):
    """Элемент коллекции.

    Attributes:
        id: ID элемента.
        user_id: ID пользователя.
        item_status: Статус элемента (liked).
        last_modified: Дата последнего изменения.
        collection_last_modified: Дата изменения в коллекции.
        likes_count: Количество лайков.
    """

    client: Optional["ClientType"] = None
    id: Optional[str] = None
    user_id: Optional[str] = None
    item_status: Optional[CollectionItemStatus] = None
    last_modified: Optional[str] = None
    collection_last_modified: Optional[str] = None
    likes_count: Optional[int] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id, self.user_id)

    def is_liked(self) -> bool:
        """Проверка, лайкнут ли элемент."""
        return self.item_status == CollectionItemStatus.LIKED

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "item_status" in data and data["item_status"]:
            try:
                data["item_status"] = CollectionItemStatus(data["item_status"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data, client))


@model
class Collection(ZvukMusicModel):
    """Коллекция пользователя.

    Attributes:
        artists: Лайкнутые артисты.
        episodes: Лайкнутые эпизоды.
        podcasts: Лайкнутые подкасты.
        playlists: Лайкнутые плейлисты.
        synthesis_playlists: Синтез-плейлисты.
        profiles: Подписки на профили.
        releases: Лайкнутые релизы.
        tracks: Лайкнутые треки.
    """

    client: Optional["ClientType"] = None
    artists: List[CollectionItem] = None  # type: ignore[assignment]
    episodes: List[CollectionItem] = None  # type: ignore[assignment]
    podcasts: List[CollectionItem] = None  # type: ignore[assignment]
    playlists: List[CollectionItem] = None  # type: ignore[assignment]
    synthesis_playlists: List[CollectionItem] = None  # type: ignore[assignment]
    profiles: List[CollectionItem] = None  # type: ignore[assignment]
    releases: List[CollectionItem] = None  # type: ignore[assignment]
    tracks: List[CollectionItem] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.artists is None:
            self.artists = []
        if self.episodes is None:
            self.episodes = []
        if self.podcasts is None:
            self.podcasts = []
        if self.playlists is None:
            self.playlists = []
        if self.synthesis_playlists is None:
            self.synthesis_playlists = []
        if self.profiles is None:
            self.profiles = []
        if self.releases is None:
            self.releases = []
        if self.tracks is None:
            self.tracks = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        for field in [
            "artists",
            "episodes",
            "podcasts",
            "playlists",
            "synthesis_playlists",
            "profiles",
            "releases",
            "tracks",
        ]:
            if field in data:
                data[field] = CollectionItem.de_list(data[field], client)

        return cls(client=client, **cls.cleanup_data(data, client))


@model
class HiddenCollection(ZvukMusicModel):
    """Скрытые элементы.

    Attributes:
        tracks: Скрытые треки.
        artists: Скрытые артисты.
    """

    client: Optional["ClientType"] = None
    tracks: List[CollectionItem] = None  # type: ignore[assignment]
    artists: List[CollectionItem] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.tracks is None:
            self.tracks = []
        if self.artists is None:
            self.artists = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "tracks" in data:
            data["tracks"] = CollectionItem.de_list(data["tracks"], client)
        if "artists" in data:
            data["artists"] = CollectionItem.de_list(data["artists"], client)

        return cls(client=client, **cls.cleanup_data(data, client))
