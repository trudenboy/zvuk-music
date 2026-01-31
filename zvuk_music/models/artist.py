"""Artist models.

Note (RU): Модели артиста.
"""

from __future__ import annotations

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

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
    """Brief artist information.

    Attributes:
        id: Artist ID.
        title: Artist name.
        image: Image.

    Note (RU): Краткая информация об артисте.
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

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_full_info(self) -> Optional["Artist"]:
        """Get full artist information.

        Returns:
            Full artist information or None.

        Note (RU): Получить полную информацию об артисте.
        """
        if self.valid_client(self.client):
            return self.client.get_artist(self.id)
        return None

    async def get_full_info_async(self) -> Optional["Artist"]:
        """Get full artist information (async).

        Returns:
            Full artist information or None.

        Note (RU): Получить полную информацию об артисте (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.get_artist(self.id)
        return None


@model
class Artist(ZvukMusicModel):
    """Full artist information.

    Attributes:
        id: Artist ID.
        title: Artist name.
        image: Primary image.
        second_image: Secondary image.
        search_title: Search title.
        description: Artist description.
        has_page: Whether the artist has a page.
        animation: Animation.
        collection_item_data: Like data.
        releases: Artist releases.
        popular_tracks: Popular tracks.
        related_artists: Related artists.

    Note (RU): Полная информация об артисте.
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
    releases: List["SimpleRelease"] = field(default_factory=list)
    popular_tracks: List["SimpleTrack"] = field(default_factory=list)
    related_artists: List[SimpleArtist] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        # Deferred import to avoid circular dependencies
        from zvuk_music.models.release import SimpleRelease
        from zvuk_music.models.track import SimpleTrack

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "second_image" in data_dict:
            data_dict["second_image"] = Image.de_json(data_dict["second_image"], client)
        if "animation" in data_dict:
            data_dict["animation"] = Animation.de_json(data_dict["animation"], client)
        if "collection_item_data" in data_dict:
            data_dict["collection_item_data"] = CollectionItem.de_json(
                data_dict["collection_item_data"], client
            )
        if "releases" in data_dict:
            data_dict["releases"] = SimpleRelease.de_list(data_dict["releases"], client)
        if "popular_tracks" in data_dict:
            data_dict["popular_tracks"] = SimpleTrack.de_list(data_dict["popular_tracks"], client)
        if "related_artists" in data_dict:
            data_dict["related_artists"] = SimpleArtist.de_list(
                data_dict["related_artists"], client
            )

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def is_liked(self) -> bool:
        """Check if the artist is liked.

        Note (RU): Проверка, лайкнут ли артист.
        """
        if self.collection_item_data:
            return self.collection_item_data.is_liked()
        return False

    def like(self) -> bool:
        """Add artist to collection.

        Returns:
            Whether the operation was successful.

        Note (RU): Добавить артиста в коллекцию.
        """
        if self.valid_client(self.client):
            return self.client.like_artist(self.id)
        return False

    def unlike(self) -> bool:
        """Remove artist from collection.

        Returns:
            Whether the operation was successful.

        Note (RU): Убрать артиста из коллекции.
        """
        if self.valid_client(self.client):
            return self.client.unlike_artist(self.id)
        return False

    async def like_async(self) -> bool:
        """Add artist to collection (async).

        Note (RU): Добавить артиста в коллекцию (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.like_artist(self.id)
        return False

    async def unlike_async(self) -> bool:
        """Remove artist from collection (async).

        Note (RU): Убрать артиста из коллекции (async).
        """
        if self.valid_async_client(self.client):
            return await self.client.unlike_artist(self.id)
        return False
