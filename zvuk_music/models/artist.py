"""Модели артиста."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.collection import CollectionItem
from zvuk_music.models.common import Animation, Image
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType
    from zvuk_music.models.release import SimpleRelease
    from zvuk_music.models.track import SimpleTrack


@model
class SimpleArtist(ZvukMusicModel):
    """Краткая информация об артисте.

    Attributes:
        id: ID артиста.
        title: Название/имя артиста.
        image: Изображение.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    image: Optional[Image] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)

        return cls(client=client, **cls.cleanup_data(data, client))

    def get_full_info(self) -> Optional["Artist"]:
        """Получить полную информацию об артисте.

        Returns:
            Полная информация об артисте или None.
        """
        if self.valid_client(self.client):
            return self.client.get_artist(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Artist"]:
        """Получить полную информацию об артисте (async).

        Returns:
            Полная информация об артисте или None.
        """
        if self.valid_async_client(self.client):
            return await self.client.get_artist(self.id)
        return None


@model
class Artist(ZvukMusicModel):
    """Полная информация об артисте.

    Attributes:
        id: ID артиста.
        title: Название/имя артиста.
        image: Основное изображение.
        second_image: Дополнительное изображение.
        search_title: Название для поиска.
        description: Описание артиста.
        has_page: Есть ли страница артиста.
        animation: Анимация.
        collection_item_data: Данные о лайке.
        releases: Релизы артиста.
        popular_tracks: Популярные треки.
        related_artists: Похожие артисты.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    image: Optional[Image] = None
    second_image: Optional[Image] = None
    search_title: Optional[str] = None
    description: Optional[str] = None
    has_page: Optional[bool] = None
    animation: Optional[Animation] = None
    collection_item_data: Optional[CollectionItem] = None
    releases: List["SimpleRelease"] = None  # type: ignore[assignment]
    popular_tracks: List["SimpleTrack"] = None  # type: ignore[assignment]
    related_artists: List[SimpleArtist] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.releases is None:
            self.releases = []
        if self.popular_tracks is None:
            self.popular_tracks = []
        if self.related_artists is None:
            self.related_artists = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        # Отложенный импорт для избежания циклических зависимостей
        from zvuk_music.models.release import SimpleRelease
        from zvuk_music.models.track import SimpleTrack

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)
        if "second_image" in data:
            data["second_image"] = Image.de_json(data["second_image"], client)
        if "animation" in data:
            data["animation"] = Animation.de_json(data["animation"], client)
        if "collection_item_data" in data:
            data["collection_item_data"] = CollectionItem.de_json(
                data["collection_item_data"], client
            )
        if "releases" in data:
            data["releases"] = SimpleRelease.de_list(data["releases"], client)
        if "popular_tracks" in data:
            data["popular_tracks"] = SimpleTrack.de_list(data["popular_tracks"], client)
        if "related_artists" in data:
            data["related_artists"] = SimpleArtist.de_list(data["related_artists"], client)

        return cls(client=client, **cls.cleanup_data(data, client))

    def is_liked(self) -> bool:
        """Проверка, лайкнут ли артист."""
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

    def like(self) -> bool:
        """Добавить артиста в коллекцию.

        Returns:
            Успешность операции.
        """
        if self.valid_client(self.client):
            return self.client.like_artist(self.id)
        return False

    def unlike(self) -> bool:
        """Убрать артиста из коллекции.

        Returns:
            Успешность операции.
        """
        if self.valid_client(self.client):
            return self.client.unlike_artist(self.id)
        return False

    async def like_async(self) -> bool:
        """Добавить артиста в коллекцию (async)."""
        if self.valid_async_client(self.client):
            return await self.client.like_artist(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Убрать артиста из коллекции (async)."""
        if self.valid_async_client(self.client):
            return await self.client.unlike_artist(self.id)
        return False
