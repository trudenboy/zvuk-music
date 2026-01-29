"""Модели релиза."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

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
    """Краткая информация о релизе.

    Attributes:
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
    artists: List[SimpleArtist] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.artists is None:
            self.artists = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)
        if "artists" in data:
            data["artists"] = SimpleArtist.de_list(data["artists"], client)
        if "type" in data and data["type"]:
            try:
                data["type"] = ReleaseType(data["type"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data, client))

    def get_year(self) -> Optional[int]:
        """Получить год выхода.

        Returns:
            Год выхода или None.
        """
        if self.date:
            try:
                return int(self.date[:4])
            except (ValueError, IndexError):
                pass
        return None

    def get_full_info(self) -> Optional["Release"]:
        """Получить полную информацию о релизе.

        Returns:
            Полная информация или None.
        """
        if self.valid_client(self.client):
            return self.client.get_release(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Release"]:
        """Получить полную информацию о релизе (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_release(self.id)
        return None


@model
class Release(ZvukMusicModel):
    """Полная информация о релизе.

    Attributes:
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
    genres: List[Genre] = None  # type: ignore[assignment]
    label: Optional[Label] = None
    artists: List[SimpleArtist] = None  # type: ignore[assignment]
    tracks: List["SimpleTrack"] = None  # type: ignore[assignment]
    related: List[SimpleRelease] = None  # type: ignore[assignment]
    collection_item_data: Optional[CollectionItem] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.genres is None:
            self.genres = []
        if self.artists is None:
            self.artists = []
        if self.tracks is None:
            self.tracks = []
        if self.related is None:
            self.related = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        from zvuk_music.models.track import SimpleTrack

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)
        if "genres" in data:
            data["genres"] = Genre.de_list(data["genres"], client)
        if "label" in data:
            data["label"] = Label.de_json(data["label"], client)
        if "artists" in data:
            data["artists"] = SimpleArtist.de_list(data["artists"], client)
        if "tracks" in data:
            data["tracks"] = SimpleTrack.de_list(data["tracks"], client)
        if "related" in data:
            data["related"] = SimpleRelease.de_list(data["related"], client)
        if "collection_item_data" in data:
            data["collection_item_data"] = CollectionItem.de_json(
                data["collection_item_data"], client
            )
        if "type" in data and data["type"]:
            try:
                data["type"] = ReleaseType(data["type"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data, client))

    def get_year(self) -> Optional[int]:
        """Получить год выхода."""
        if self.date:
            try:
                return int(self.date[:4])
            except (ValueError, IndexError):
                pass
        return None

    def get_cover_url(self, size: int = 300) -> str:
        """Получить URL обложки.

        Args:
            size: Размер изображения.

        Returns:
            URL обложки.
        """
        if self.image:
            return self.image.get_url(size, size)
        return ""

    def is_liked(self) -> bool:
        """Проверка, лайкнут ли релиз."""
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

    def like(self) -> bool:
        """Добавить релиз в коллекцию."""
        if self.valid_client(self.client):
            return self.client.like_release(self.id)
        return False

    def unlike(self) -> bool:
        """Убрать релиз из коллекции."""
        if self.valid_client(self.client):
            return self.client.unlike_release(self.id)
        return False

    async def like_async(self) -> bool:
        """Добавить релиз в коллекцию (async)."""
        if self.valid_async_client(self.client):
            return await self.client.like_release(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Убрать релиз из коллекции (async)."""
        if self.valid_async_client(self.client):
            return await self.client.unlike_release(self.id)
        return False
