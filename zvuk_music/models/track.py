"""Модели трека."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.enums import Quality
from zvuk_music.models.artist import SimpleArtist
from zvuk_music.models.collection import CollectionItem
from zvuk_music.models.common import Genre
from zvuk_music.models.release import SimpleRelease
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType
    from zvuk_music.models.stream import Stream


@model
class SimpleTrack(ZvukMusicModel):
    """Краткая информация о треке.

    Attributes:
        id: ID трека.
        title: Название.
        duration: Длительность в секундах.
        explicit: Explicit содержимое.
        artists: Артисты.
        release: Релиз.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    duration: int = 0
    explicit: bool = False
    artists: List[SimpleArtist] = None  # type: ignore[assignment]
    release: Optional[SimpleRelease] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.artists is None:
            self.artists = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "artists" in data_dict:
            data_dict["artists"] = SimpleArtist.de_list(data_dict["artists"], client)
        if "release" in data_dict:
            data_dict["release"] = SimpleRelease.de_json(data_dict["release"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_duration_str(self) -> str:
        """Получить длительность в формате MM:SS.

        Returns:
            Строка длительности.
        """
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def get_artists_str(self) -> str:
        """Получить строку с именами артистов.

        Returns:
            Имена артистов через запятую.
        """
        return ", ".join(a.title for a in self.artists)

    def get_full_info(self) -> Optional["Track"]:
        """Получить полную информацию о треке.

        Returns:
            Полная информация или None.
        """
        if self.valid_client(self.client):
            return self.client.get_track(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Track"]:
        """Получить полную информацию о треке (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_track(self.id)
        return None


@model
class Track(ZvukMusicModel):
    """Полная информация о треке.

    Attributes:
        id: ID трека.
        title: Название.
        search_title: Название для поиска.
        position: Позиция в релизе.
        duration: Длительность в секундах.
        availability: Доступность.
        artist_template: Шаблон имени артиста.
        condition: Состояние.
        explicit: Explicit содержимое.
        lyrics: Текст песни.
        zchan: Канал.
        has_flac: Доступен ли FLAC.
        artist_names: Имена артистов.
        credits: Авторы.
        genres: Жанры.
        artists: Артисты.
        release: Релиз.
        collection_item_data: Данные о лайке.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    search_title: Optional[str] = None
    position: Optional[int] = None
    duration: int = 0
    availability: int = 0
    artist_template: Optional[str] = None
    condition: Optional[str] = None
    explicit: bool = False
    lyrics: Optional[Any] = None
    zchan: Optional[str] = None
    has_flac: bool = False
    artist_names: List[str] = None  # type: ignore[assignment]
    credits: Optional[str] = None
    genres: List[Genre] = None  # type: ignore[assignment]
    artists: List[SimpleArtist] = None  # type: ignore[assignment]
    release: Optional[SimpleRelease] = None
    collection_item_data: Optional[CollectionItem] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.artist_names is None:
            self.artist_names = []
        if self.genres is None:
            self.genres = []
        if self.artists is None:
            self.artists = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "genres" in data_dict:
            data_dict["genres"] = Genre.de_list(data_dict["genres"], client)
        if "artists" in data_dict:
            data_dict["artists"] = SimpleArtist.de_list(data_dict["artists"], client)
        if "release" in data_dict:
            data_dict["release"] = SimpleRelease.de_json(data_dict["release"], client)
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

    def get_artists_str(self) -> str:
        """Получить строку с именами артистов."""
        if self.artists:
            return ", ".join(a.title for a in self.artists)
        return ", ".join(self.artist_names)

    def get_cover_url(self, size: int = 300) -> str:
        """Получить URL обложки.

        Args:
            size: Размер изображения.

        Returns:
            URL обложки.
        """
        if self.release and self.release.image:
            return self.release.image.get_url(size, size)
        return ""

    def is_liked(self) -> bool:
        """Проверка, лайкнут ли трек."""
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

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

    def get_stream(self) -> Optional["Stream"]:
        """Получить объект Stream с URL и временем истечения.

        Returns:
            Объект Stream или None.
        """
        if self.valid_client(self.client):
            streams = self.client.get_stream_urls([self.id])
            if streams:
                return streams[0]
        return None

    async def get_stream_async(self) -> Optional["Stream"]:
        """Получить объект Stream (async)."""
        if self.valid_async_client(self.client):
            streams = await self.client.get_stream_urls([self.id])
            if streams:
                return streams[0]
        return None

    def download(self, filename: str, quality: Quality = Quality.HIGH) -> None:
        """Скачать трек.

        Args:
            filename: Путь для сохранения.
            quality: Качество аудио.
        """
        if self.valid_client(self.client):
            url = self.get_stream_url(quality)
            self.client._request.download(url, filename)

    async def download_async(self, filename: str, quality: Quality = Quality.HIGH) -> None:
        """Скачать трек (async).

        Args:
            filename: Путь для сохранения.
            quality: Качество аудио.
        """
        if self.valid_async_client(self.client):
            url = await self.get_stream_url_async(quality)
            await self.client._request.download(url, filename)

    def like(self) -> bool:
        """Добавить трек в коллекцию."""
        if self.valid_client(self.client):
            return self.client.like_track(self.id)
        return False

    def unlike(self) -> bool:
        """Убрать трек из коллекции."""
        if self.valid_client(self.client):
            return self.client.unlike_track(self.id)
        return False

    def hide(self) -> bool:
        """Скрыть трек."""
        if self.valid_client(self.client):
            return self.client.hide_track(self.id)
        return False

    def unhide(self) -> bool:
        """Убрать трек из скрытых."""
        if self.valid_client(self.client):
            return self.client.unhide_track(self.id)
        return False

    async def like_async(self) -> bool:
        """Добавить трек в коллекцию (async)."""
        if self.valid_async_client(self.client):
            return await self.client.like_track(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Убрать трек из коллекции (async)."""
        if self.valid_async_client(self.client):
            return await self.client.unlike_track(self.id)
        return False

    async def hide_async(self) -> bool:
        """Скрыть трек (async)."""
        if self.valid_async_client(self.client):
            return await self.client.hide_track(self.id)
        return False

    async def unhide_async(self) -> bool:
        """Убрать трек из скрытых (async)."""
        if self.valid_async_client(self.client):
            return await self.client.unhide_track(self.id)
        return False
