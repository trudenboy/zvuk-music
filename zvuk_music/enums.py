"""Enumerations for the Zvuk Music API library.

Note (RU): Перечисления библиотеки Zvuk Music API.
"""

from enum import Enum


class Quality(str, Enum):
    """Audio quality.

    Note (RU): Качество аудио.
    """

    MID = "mid"  # 128kbps MP3, always available
    HIGH = "high"  # 320kbps MP3, requires subscription
    FLAC = "flacdrm"  # FLAC with DRM, requires subscription


class ReleaseType(str, Enum):
    """Release type.

    Note (RU): Тип релиза.
    """

    ALBUM = "album"
    SINGLE = "single"
    EP = "ep"
    COMPILATION = "compilation"


class CollectionItemType(str, Enum):
    """Collection item type.

    Note (RU): Тип элемента коллекции.
    """

    TRACK = "track"
    RELEASE = "release"
    ARTIST = "artist"
    PODCAST = "podcast"
    EPISODE = "episode"
    PLAYLIST = "playlist"
    PROFILE = "profile"


class CollectionItemStatus(str, Enum):
    """Collection item status.

    Note (RU): Статус элемента в коллекции.
    """

    LIKED = "liked"


class OrderBy(str, Enum):
    """Sort by field.

    Note (RU): Сортировка по полю.
    """

    ALPHABET = "alphabet"  # Alphabetical
    ARTIST = "artist"  # By artist name
    DATE_ADDED = "dateAdded"  # By date added


class OrderDirection(str, Enum):
    """Sort direction.

    Note (RU): Направление сортировки.
    """

    ASC = "asc"  # Ascending
    DESC = "desc"  # Descending


class Typename(str, Enum):
    """GraphQL entity type.

    Note (RU): Тип сущности GraphQL.
    """

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
    """Background type.

    Note (RU): Тип фона.
    """

    IMAGE = "image"
