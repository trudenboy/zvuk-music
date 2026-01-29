"""Перечисления библиотеки Zvuk Music API."""

from enum import Enum


class Quality(str, Enum):
    """Качество аудио."""

    MID = "mid"  # 128kbps MP3, всегда доступен
    HIGH = "high"  # 320kbps MP3, требует подписку
    FLAC = "flacdrm"  # FLAC с DRM, требует подписку


class ReleaseType(str, Enum):
    """Тип релиза."""

    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
    COMPILATION = "compilation"


class CollectionItemType(str, Enum):
    """Тип элемента коллекции."""

    TRACK = "track"
    RELEASE = "release"
    ARTIST = "artist"
    PODCAST = "podcast"
    EPISODE = "episode"
    PLAYLIST = "playlist"
    PROFILE = "profile"


class CollectionItemStatus(str, Enum):
    """Статус элемента в коллекции."""

    LIKED = "liked"


class OrderBy(str, Enum):
    """Сортировка по полю."""

    ALPHABET = "alphabet"  # По алфавиту
    ARTIST = "artist"  # По имени артиста
    DATE_ADDED = "dateAdded"  # По дате добавления


class OrderDirection(str, Enum):
    """Направление сортировки."""

    ASC = "asc"  # По возрастанию
    DESC = "desc"  # По убыванию


class Typename(str, Enum):
    """Тип сущности GraphQL."""

    ARTIST = "Artist"
    TRACK = "Track"
    RELEASE = "Release"
    PLAYLIST = "Playlist"
    EPISODE = "Episode"
    PODCAST = "Podcast"
    PROFILE = "Profile"
    BOOK = "Book"
    CHAPTER = "Chapter"


class BackgroundType(str, Enum):
    """Тип фона."""

    IMAGE = "image"
