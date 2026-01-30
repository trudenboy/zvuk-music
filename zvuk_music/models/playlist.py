"""Модели плейлиста."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.common import Image
from zvuk_music.models.track import SimpleTrack
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class PlaylistItem(ZvukMusicModel):
    """Элемент плейлиста.

    Attributes:
        type: Тип элемента.
        item_id: ID элемента.
    """

    client: Optional["ClientType"] = None
    type: str = "track"
    item_id: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.type, self.item_id)


@model
class SimplePlaylist(ZvukMusicModel):
    """Краткая информация о плейлисте.

    Attributes:
        id: ID плейлиста.
        title: Название.
        is_public: Публичный ли.
        description: Описание.
        duration: Общая длительность.
        image: Обложка.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    is_public: bool = True
    description: Optional[str] = None
    duration: int = 0
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

    def get_full_info(self) -> Optional["Playlist"]:
        """Получить полную информацию о плейлисте."""
        if self.valid_client(self.client):
            return self.client.get_playlist(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Playlist"]:
        """Получить полную информацию о плейлисте (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_playlist(self.id)
        return None


@model
class Playlist(ZvukMusicModel):
    """Полная информация о плейлисте.

    Attributes:
        id: ID плейлиста.
        title: Название.
        user_id: ID владельца.
        is_public: Публичный ли.
        is_deleted: Удалён ли.
        shared: Расшарен ли.
        branded: Брендированный ли.
        description: Описание.
        duration: Общая длительность.
        image: Обложка.
        updated: Дата обновления.
        search_title: Название для поиска.
        tracks: Треки.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    user_id: Optional[str] = None
    is_public: bool = True
    is_deleted: bool = False
    shared: bool = False
    branded: bool = False
    description: Optional[str] = None
    duration: int = 0
    image: Optional[Image] = None
    updated: Optional[str] = None
    search_title: Optional[str] = None
    tracks: List[SimpleTrack] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.tracks is None:
            self.tracks = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "tracks" in data_dict:
            data_dict["tracks"] = SimpleTrack.de_list(data_dict["tracks"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_tracks_paginated(self, limit: int = 50, offset: int = 0) -> List[SimpleTrack]:
        """Получить треки с пагинацией.

        Args:
            limit: Количество треков.
            offset: Смещение.

        Returns:
            Список треков.
        """
        if self.valid_client(self.client):
            return self.client.get_playlist_tracks(self.id, limit, offset)
        return []

    async def get_tracks_paginated_async(
        self, limit: int = 50, offset: int = 0
    ) -> List[SimpleTrack]:
        """Получить треки с пагинацией (async)."""
        if self.valid_async_client(self.client):
            return await self.client.get_playlist_tracks(self.id, limit, offset)
        return []

    def rename(self, new_name: str) -> bool:
        """Переименовать плейлист.

        Args:
            new_name: Новое название.

        Returns:
            Успешность операции.
        """
        if self.valid_client(self.client):
            result = self.client.rename_playlist(self.id, new_name)
            if result:
                self.title = new_name
            return result
        return False

    async def rename_async(self, new_name: str) -> bool:
        """Переименовать плейлист (async)."""
        if self.valid_async_client(self.client):
            result = await self.client.rename_playlist(self.id, new_name)
            if result:
                self.title = new_name
            return result
        return False

    def delete(self) -> bool:
        """Удалить плейлист."""
        if self.valid_client(self.client):
            return self.client.delete_playlist(self.id)
        return False

    async def delete_async(self) -> bool:
        """Удалить плейлист (async)."""
        if self.valid_async_client(self.client):
            return await self.client.delete_playlist(self.id)
        return False

    def add_tracks(self, track_ids: List[str]) -> bool:
        """Добавить треки в плейлист.

        Args:
            track_ids: ID треков для добавления.

        Returns:
            Успешность операции.
        """
        if self.valid_client(self.client):
            return self.client.add_tracks_to_playlist(self.id, track_ids)
        return False

    async def add_tracks_async(self, track_ids: List[str]) -> bool:
        """Добавить треки в плейлист (async)."""
        if self.valid_async_client(self.client):
            return await self.client.add_tracks_to_playlist(self.id, track_ids)
        return False

    def set_public(self, is_public: bool) -> bool:
        """Изменить видимость плейлиста.

        Args:
            is_public: Публичный или приватный.

        Returns:
            Успешность операции.
        """
        if self.valid_client(self.client):
            result = self.client.set_playlist_public(self.id, is_public)
            if result:
                self.is_public = is_public
            return result
        return False

    async def set_public_async(self, is_public: bool) -> bool:
        """Изменить видимость плейлиста (async)."""
        if self.valid_async_client(self.client):
            result = await self.client.set_playlist_public(self.id, is_public)
            if result:
                self.is_public = is_public
            return result
        return False


@model
class PlaylistAuthor(ZvukMusicModel):
    """Автор плейлиста.

    Attributes:
        id: ID автора.
        name: Имя.
        image: Изображение.
        matches: Совпадение (score).
    """

    client: Optional["ClientType"] = None
    id: str = ""
    name: str = ""
    image: Optional[Image] = None
    matches: Optional[float] = None

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


@model
class SynthesisPlaylist(ZvukMusicModel):
    """Синтез-плейлист.

    Attributes:
        id: ID плейлиста.
        tracks: Треки.
        authors: Авторы.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    tracks: List[SimpleTrack] = None  # type: ignore[assignment]
    authors: List[PlaylistAuthor] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.tracks is None:
            self.tracks = []
        if self.authors is None:
            self.authors = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "tracks" in data_dict:
            data_dict["tracks"] = SimpleTrack.de_list(data_dict["tracks"], client)
        if "authors" in data_dict:
            data_dict["authors"] = PlaylistAuthor.de_list(data_dict["authors"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))
