"""Enumerations for the Zvuk Music API library.

Note (RU): Перечисления библиотеки Zvuk Music API.
"""

from enum import Enum


class Quality(str, Enum):
    """Audio quality for GraphQL DRM-wrapped streaming.

    For direct (non-DRM) streaming via Tiny API, use StreamQuality instead.

    Note (RU): Качество аудио для GraphQL DRM-стриминга.
        Для прямого стриминга (без DRM) через Tiny API используйте StreamQuality.
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


class StreamQuality(str, Enum):
    """Direct stream quality (non-DRM) for Tiny API.

    For GraphQL DRM-wrapped streaming, use Quality instead.

    Note (RU): Качество прямого стрима (без DRM) для Tiny API.
        Для GraphQL DRM-стриминга используйте Quality.
    """

    MID = "mid"
    HIGH = "high"
    FLAC = "flac"


class LyricsType(str, Enum):
    """Lyrics format type.

    Note (RU): Тип формата текста песни.
    """

    SUBTITLE = "subtitle"
    LYRICS = "lyrics"


class BackgroundType(str, Enum):
    """Background type.

    Note (RU): Тип фона.
    """

    IMAGE = "image"
