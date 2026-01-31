"""Модели коллекции (лайки, скрытые)."""

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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

        data_dict: Dict[str, Any] = data.copy()

        if "item_status" in data_dict and data_dict["item_status"]:
            try:
                data_dict["item_status"] = CollectionItemStatus(data_dict["item_status"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data_dict, client))


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
    artists: List[CollectionItem] = field(default_factory=list)
    episodes: List[CollectionItem] = field(default_factory=list)
    podcasts: List[CollectionItem] = field(default_factory=list)
    playlists: List[CollectionItem] = field(default_factory=list)
    synthesis_playlists: List[CollectionItem] = field(default_factory=list)
    profiles: List[CollectionItem] = field(default_factory=list)
    releases: List[CollectionItem] = field(default_factory=list)
    tracks: List[CollectionItem] = field(default_factory=list)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        for field_name in [
            "artists",
            "episodes",
            "podcasts",
            "playlists",
            "synthesis_playlists",
            "profiles",
            "releases",
            "tracks",
        ]:
            if field_name in data_dict:
                data_dict[field_name] = CollectionItem.de_list(data_dict[field_name], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))


@model
class HiddenCollection(ZvukMusicModel):
    """Скрытые элементы.

    Attributes:
        tracks: Скрытые треки.
        artists: Скрытые артисты.
    """

    client: Optional["ClientType"] = None
    tracks: List[CollectionItem] = field(default_factory=list)
    artists: List[CollectionItem] = field(default_factory=list)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "tracks" in data_dict:
            data_dict["tracks"] = CollectionItem.de_list(data_dict["tracks"], client)
        if "artists" in data_dict:
            data_dict["artists"] = CollectionItem.de_list(data_dict["artists"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))
