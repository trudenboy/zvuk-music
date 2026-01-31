"""Playlist models.

Note (RU): Модели плейлиста.
"""

from __future__ import annotations

from dataclasses import field
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
    """Playlist item.

    Attributes:
        type: Item type.
        item_id: Item ID.

    Note (RU): Элемент плейлиста.
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
    """Brief playlist information.

    Attributes:
        id: Playlist ID.
        title: Title.
        is_public: Whether public.
        description: Description.
        duration: Total duration.
        image: Cover image.

    Note (RU): Краткая информация о плейлисте.
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
        """Get full playlist information.

        Note (RU): Получить полную информацию о плейлисте.
        """
        if self.valid_client(self.client):
            return self.client.get_playlist(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Playlist"]:
        """Get full playlist information (async).

        Note (RU): Получить полную информацию о плейлисте (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.get_playlist(self.id)
        return None


@model
class Playlist(ZvukMusicModel):
    """Full playlist information.

    Attributes:
        id: Playlist ID.
        title: Title.
        user_id: Owner ID.
        is_public: Whether public.
        is_deleted: Whether deleted.
        shared: Whether shared.
        branded: Whether branded.
        description: Description.
        duration: Total duration.
        image: Cover image.
        updated: Update date.
        search_title: Search title.
        tracks: Tracks.

    Note (RU): Полная информация о плейлисте.
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
    tracks: List[SimpleTrack] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

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
        """Get tracks with pagination.

        Args:
            limit: Number of tracks.
            offset: Offset.

        Returns:
            List of tracks.

        Note (RU): Получить треки с пагинацией.
            Args: limit: Количество треков. offset: Смещение.
            Returns: Список треков.
        """
        if self.valid_client(self.client):
            return self.client.get_playlist_tracks(self.id, limit, offset)
        return []

    async def get_tracks_paginated_async(
        self, limit: int = 50, offset: int = 0
    ) -> List[SimpleTrack]:
        """Get tracks with pagination (async).

        Note (RU): Получить треки с пагинацией (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.get_playlist_tracks(self.id, limit, offset)
        return []

    def rename(self, new_name: str) -> bool:
        """Rename playlist.

        Args:
            new_name: New name.

        Returns:
            Whether the operation succeeded.

        Note (RU): Переименовать плейлист.
            Args: new_name: Новое название.
            Returns: Успешность операции.
        """
        if self.valid_client(self.client):
            result = self.client.rename_playlist(self.id, new_name)
            if result:
                self.title = new_name
            return result
        return False

    async def rename_async(self, new_name: str) -> bool:
        """Rename playlist (async).

        Note (RU): Переименовать плейлист (async).
        """
        if self.valid_async_client(self.client):
            result = await self.client.rename_playlist(self.id, new_name)
            if result:
                self.title = new_name
            return result
        return False

    def delete(self) -> bool:
        """Delete playlist.

        Note (RU): Удалить плейлист.
        """
        if self.valid_client(self.client):
            return self.client.delete_playlist(self.id)
        return False

    async def delete_async(self) -> bool:
        """Delete playlist (async).

        Note (RU): Удалить плейлист (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.delete_playlist(self.id)
        return False

    def add_tracks(self, track_ids: List[str]) -> bool:
        """Add tracks to playlist.

        Args:
            track_ids: Track IDs to add.

        Returns:
            Whether the operation succeeded.

        Note (RU): Добавить треки в плейлист.
            Args: track_ids: ID треков для добавления.
            Returns: Успешность операции.
        """
        if self.valid_client(self.client):
            return self.client.add_tracks_to_playlist(self.id, track_ids)
        return False

    async def add_tracks_async(self, track_ids: List[str]) -> bool:
        """Add tracks to playlist (async).

        Note (RU): Добавить треки в плейлист (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.add_tracks_to_playlist(self.id, track_ids)
        return False

    def set_public(self, is_public: bool) -> bool:
        """Change playlist visibility.

        Args:
            is_public: Public or private.

        Returns:
            Whether the operation succeeded.

        Note (RU): Изменить видимость плейлиста.
            Args: is_public: Публичный или приватный.
            Returns: Успешность операции.
        """
        if self.valid_client(self.client):
            result = self.client.set_playlist_public(self.id, is_public)
            if result:
                self.is_public = is_public
            return result
        return False

    async def set_public_async(self, is_public: bool) -> bool:
        """Change playlist visibility (async).

        Note (RU): Изменить видимость плейлиста (async).
        """
        if self.valid_async_client(self.client):
            result = await self.client.set_playlist_public(self.id, is_public)
            if result:
                self.is_public = is_public
            return result
        return False


@model
class PlaylistAuthor(ZvukMusicModel):
    """Playlist author.

    Attributes:
        id: Author ID.
        name: Name.
        image: Image.
        matches: Match (score).

    Note (RU): Автор плейлиста.
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
    """Synthesis playlist.

    Attributes:
        id: Playlist ID.
        tracks: Tracks.
        authors: Authors.

    Note (RU): Синтез-плейлист.
        id: ID плейлиста.
        tracks: Треки.
        authors: Авторы.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    tracks: List[SimpleTrack] = field(default_factory=list)
    authors: List[PlaylistAuthor] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

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
