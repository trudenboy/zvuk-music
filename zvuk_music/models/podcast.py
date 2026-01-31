"""Модели подкастов."""

from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.enums import Quality
from zvuk_music.models.collection import CollectionItem
from zvuk_music.models.common import Image
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class PodcastAuthor(ZvukMusicModel):
    """Автор подкаста.

    Attributes:
        id: ID автора.
        name: Имя.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    name: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)


@model
class SimplePodcast(ZvukMusicModel):
    """Краткая информация о подкасте.

    Attributes:
        id: ID подкаста.
        title: Название.
        explicit: Explicit содержимое.
        image: Обложка.
        authors: Авторы.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    explicit: bool = False
    image: Optional[Image] = None
    authors: List[PodcastAuthor] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "authors" in data_dict:
            data_dict["authors"] = PodcastAuthor.de_list(data_dict["authors"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_full_info(self) -> Optional["Podcast"]:
        """Получить полную информацию о подкасте."""
        if self.valid_client(self.client):
            return self.client.get_podcast(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Podcast"]:
        """Получить полную информацию о подкасте (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_podcast(self.id)
        return None


@model
class Podcast(ZvukMusicModel):
    """Полная информация о подкасте.

    Attributes:
        id: ID подкаста.
        title: Название.
        explicit: Explicit содержимое.
        description: Описание.
        updated_date: Дата обновления.
        availability: Доступность.
        type: Тип подкаста.
        image: Обложка.
        authors: Авторы.
        episodes: Эпизоды (только ID).
        collection_item_data: Данные о лайке.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    explicit: bool = False
    description: Optional[str] = None
    updated_date: Optional[str] = None
    availability: int = 0
    type: Optional[str] = None
    image: Optional[Image] = None
    authors: List[PodcastAuthor] = field(default_factory=list)
    episodes: List[Dict[str, Any]] = field(default_factory=list)
    collection_item_data: Optional[CollectionItem] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "authors" in data_dict:
            data_dict["authors"] = PodcastAuthor.de_list(data_dict["authors"], client)
        if "collection_item_data" in data_dict:
            data_dict["collection_item_data"] = CollectionItem.de_json(
                data_dict["collection_item_data"], client
            )

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def is_liked(self) -> bool:
        """Проверка, лайкнут ли подкаст."""
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

    def like(self) -> bool:
        """Добавить подкаст в коллекцию."""
        if self.valid_client(self.client):
            return self.client.like_podcast(self.id)
        return False

    def unlike(self) -> bool:
        """Убрать подкаст из коллекции."""
        if self.valid_client(self.client):
            return self.client.unlike_podcast(self.id)
        return False

    async def like_async(self) -> bool:
        """Добавить подкаст в коллекцию (async)."""
        if self.valid_async_client(self.client):
            return await self.client.like_podcast(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Убрать подкаст из коллекции (async)."""
        if self.valid_async_client(self.client):
            return await self.client.unlike_podcast(self.id)
        return False


@model
class SimpleEpisode(ZvukMusicModel):
    """Краткая информация об эпизоде.

    Attributes:
        id: ID эпизода.
        title: Название.
        explicit: Explicit содержимое.
        duration: Длительность в секундах.
        publication_date: Дата публикации.
        image: Обложка.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    explicit: bool = False
    duration: int = 0
    publication_date: Optional[str] = None
    image: Optional[Image] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_full_info(self) -> Optional["Episode"]:
        """Получить полную информацию об эпизоде."""
        if self.valid_client(self.client):
            return self.client.get_episode(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Episode"]:
        """Получить полную информацию об эпизоде (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_episode(self.id)
        return None


@model
class Episode(ZvukMusicModel):
    """Полная информация об эпизоде.

    Attributes:
        id: ID эпизода.
        title: Название.
        explicit: Explicit содержимое.
        description: Описание.
        duration: Длительность в секундах.
        availability: Доступность.
        publication_date: Дата публикации.
        image: Обложка.
        podcast: Подкаст.
        collection_item_data: Данные о лайке.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    explicit: bool = False
    description: Optional[str] = None
    duration: int = 0
    availability: int = 0
    publication_date: Optional[str] = None
    image: Optional[Image] = None
    podcast: Optional[SimplePodcast] = None
    collection_item_data: Optional[CollectionItem] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "podcast" in data_dict:
            data_dict["podcast"] = SimplePodcast.de_json(data_dict["podcast"], client)
        if "collection_item_data" in data_dict:
            data_dict["collection_item_data"] = CollectionItem.de_json(
                data_dict["collection_item_data"], client
            )

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_duration_str(self) -> str:
        """Получить длительность в формате MM:SS."""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def get_stream_url(self, quality: Quality = Quality.HIGH) -> str:
        """Получить URL для стриминга.

        Args:
            quality: Качество аудио.

        Returns:
            URL для скачивания/стриминга.
        """
        if self.valid_client(self.client):
            return self.client.get_stream_url(self.id, quality)
        return ""

    async def get_stream_url_async(self, quality: Quality = Quality.HIGH) -> str:
        """Получить URL для стриминга (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_stream_url(self.id, quality)
        return ""

    def download(self, filename: str, quality: Quality = Quality.HIGH) -> None:
        """Скачать эпизод.

        Args:
            filename: Путь для сохранения.
            quality: Качество аудио.
        """
        if self.valid_client(self.client):
            url = self.get_stream_url(quality)
            self.client._request.download(url, filename)

    async def download_async(self, filename: str, quality: Quality = Quality.HIGH) -> None:
        """Скачать эпизод (async)."""
        if self.valid_async_client(self.client):
            url = await self.get_stream_url_async(quality)
            await self.client._request.download(url, filename)
