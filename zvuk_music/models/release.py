"""Release models.

Note (RU): Модели релиза.
"""

from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.enums import ReleaseType
from zvuk_music.models.artist import SimpleArtist
from zvuk_music.models.collection import CollectionItem
from zvuk_music.models.common import Genre, Image, Label
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType
    from zvuk_music.models.track import SimpleTrack


@model
class SimpleRelease(ZvukMusicModel):
    """Brief release information.

    Attributes:
        id: Release ID.
        title: Title.
        date: Release date (ISO 8601).
        type: Release type.
        image: Cover image.
        explicit: Explicit content.
        artists: Artists.

    Note (RU): Краткая информация о релизе.
        id: ID релиза.
        title: Название.
        date: Дата выхода (ISO 8601).
        type: Тип релиза.
        image: Обложка.
        explicit: Explicit содержимое.
        artists: Артисты.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    date: Optional[str] = None
    type: Optional[ReleaseType] = None
    image: Optional[Image] = None
    explicit: bool = False
    artists: List[SimpleArtist] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "artists" in data_dict:
            data_dict["artists"] = SimpleArtist.de_list(data_dict["artists"], client)
        if "type" in data_dict and data_dict["type"]:
            try:
                data_dict["type"] = ReleaseType(data_dict["type"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_year(self) -> Optional[int]:
        """Get release year.

        Returns:
            Release year or None.

        Note (RU): Получить год выхода.
            Returns: Год выхода или None.
        """
        if self.date:
            try:
                return int(self.date[:4])
            except (ValueError, IndexError):
                pass
        return None

    def get_full_info(self) -> Optional["Release"]:
        """Get full release information.

        Returns:
            Full information or None.

        Note (RU): Получить полную информацию о релизе.
            Returns: Полная информация или None.
        """
        if self.valid_client(self.client):
            return self.client.get_release(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Release"]:
        """Get full release information (async).

        Note (RU): Получить полную информацию о релизе (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.get_release(self.id)
        return None


@model
class Release(ZvukMusicModel):
    """Full release information.

    Attributes:
        id: Release ID.
        title: Title.
        search_title: Search title.
        date: Release date.
        type: Release type.
        image: Cover image.
        explicit: Explicit content.
        availability: Availability.
        artist_template: Artist name template.
        genres: Genres.
        label: Label.
        artists: Artists.
        tracks: Tracks.
        related: Related releases.
        collection_item_data: Like data.

    Note (RU): Полная информация о релизе.
        id: ID релиза.
        title: Название.
        search_title: Название для поиска.
        date: Дата выхода.
        type: Тип релиза.
        image: Обложка.
        explicit: Explicit содержимое.
        availability: Доступность.
        artist_template: Шаблон имени артиста.
        genres: Жанры.
        label: Лейбл.
        artists: Артисты.
        tracks: Треки.
        related: Похожие релизы.
        collection_item_data: Данные о лайке.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    search_title: Optional[str] = None
    date: Optional[str] = None
    type: Optional[ReleaseType] = None
    image: Optional[Image] = None
    explicit: bool = False
    availability: int = 0
    artist_template: Optional[str] = None
    genres: List[Genre] = field(default_factory=list)
    label: Optional[Label] = None
    artists: List[SimpleArtist] = field(default_factory=list)
    tracks: List["SimpleTrack"] = field(default_factory=list)
    related: List[SimpleRelease] = field(default_factory=list)
    collection_item_data: Optional[CollectionItem] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        from zvuk_music.models.track import SimpleTrack

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "genres" in data_dict:
            data_dict["genres"] = Genre.de_list(data_dict["genres"], client)
        if "label" in data_dict:
            data_dict["label"] = Label.de_json(data_dict["label"], client)
        if "artists" in data_dict:
            data_dict["artists"] = SimpleArtist.de_list(data_dict["artists"], client)
        if "tracks" in data_dict:
            data_dict["tracks"] = SimpleTrack.de_list(data_dict["tracks"], client)
        if "related" in data_dict:
            data_dict["related"] = SimpleRelease.de_list(data_dict["related"], client)
        if "collection_item_data" in data_dict:
            data_dict["collection_item_data"] = CollectionItem.de_json(
                data_dict["collection_item_data"], client
            )
        if "type" in data_dict and data_dict["type"]:
            try:
                data_dict["type"] = ReleaseType(data_dict["type"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_year(self) -> Optional[int]:
        """Get release year.

        Note (RU): Получить год выхода.
        """
        if self.date:
            try:
                return int(self.date[:4])
            except (ValueError, IndexError):
                pass
        return None

    def get_cover_url(self, size: int = 300) -> str:
        """Get cover image URL.

        Args:
            size: Image size.

        Returns:
            Cover image URL.

        Note (RU): Получить URL обложки.
            Args: size: Размер изображения.
            Returns: URL обложки.
        """
        if self.image:
            return self.image.get_url(size, size)
        return ""

    def is_liked(self) -> bool:
        """Check if release is liked.

        Note (RU): Проверка, лайкнут ли релиз.
        """
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

    def like(self) -> bool:
        """Add release to collection.

        Note (RU): Добавить релиз в коллекцию.
        """
        if self.valid_client(self.client):
            return self.client.like_release(self.id)
        return False

    def unlike(self) -> bool:
        """Remove release from collection.

        Note (RU): Убрать релиз из коллекции.
        """
        if self.valid_client(self.client):
            return self.client.unlike_release(self.id)
        return False

    async def like_async(self) -> bool:
        """Add release to collection (async).

        Note (RU): Добавить релиз в коллекцию (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.like_release(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Remove release from collection (async).

        Note (RU): Убрать релиз из коллекции (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.unlike_release(self.id)
        return False
