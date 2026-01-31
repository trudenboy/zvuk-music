"""Zvuk Music API - Python library for the Zvuk.com API.

Example:
    >>> from zvuk_music import Client
    >>>
    >>> # Anonymous access
    >>> token = Client.get_anonymous_token()
    >>> client = Client(token=token)
    >>>
    >>> # Search
    >>> results = client.quick_search("Metallica")
    >>> for track in results.tracks:
    ...     print(f"{track.title} - {track.get_artists_str()}")

Note (RU): Zvuk Music API - Python библиотека для работы с API Zvuk.com.
"""

from zvuk_music.base import ZvukMusicModel, ZvukMusicObject
from zvuk_music.client import Client
from zvuk_music.enums import (
    BackgroundType,
    CollectionItemStatus,
    CollectionItemType,
    OrderBy,
    OrderDirection,
    Quality,
    ReleaseType,
    Typename,
)
from zvuk_music.exceptions import (
    BadRequestError,
    BotDetectedError,
    GraphQLError,
    NetworkError,
    NotFoundError,
    QualityNotAvailableError,
    SubscriptionRequiredError,
    TimedOutError,
    UnauthorizedError,
    ZvukMusicError,
)
from zvuk_music.models import (
    Animation,
    Artist,
    Background,
    BookAuthor,
    Collection,
    CollectionItem,
    Episode,
    ExternalProfile,
    Genre,
    HiddenCollection,
    Image,
    Label,
    Page,
    Playlist,
    PlaylistAuthor,
    PlaylistItem,
    Podcast,
    PodcastAuthor,
    Profile,
    ProfileResult,
    QuickSearch,
    Release,
    Search,
    SearchResult,
    SimpleArtist,
    SimpleBook,
    SimpleEpisode,
    SimplePlaylist,
    SimplePodcast,
    SimpleProfile,
    SimpleRelease,
    SimpleTrack,
    Stream,
    StreamUrls,
    SynthesisPlaylist,
    Track,
)

__version__ = "0.5.1"
__author__ = "Zvuk Music API"

__all__ = [
    # Client
    "Client",
    # Base
    "ZvukMusicModel",
    "ZvukMusicObject",
    # Enums
    "BackgroundType",
    "CollectionItemStatus",
    "CollectionItemType",
    "OrderBy",
    "OrderDirection",
    "Quality",
    "ReleaseType",
    "Typename",
    # Exceptions
    "BadRequestError",
    "BotDetectedError",
    "GraphQLError",
    "NetworkError",
    "NotFoundError",
    "QualityNotAvailableError",
    "SubscriptionRequiredError",
    "TimedOutError",
    "UnauthorizedError",
    "ZvukMusicError",
    # Models
    "Animation",
    "Artist",
    "Background",
    "BookAuthor",
    "Collection",
    "CollectionItem",
    "Episode",
    "ExternalProfile",
    "Genre",
    "HiddenCollection",
    "Image",
    "Label",
    "Page",
    "Playlist",
    "PlaylistAuthor",
    "PlaylistItem",
    "Podcast",
    "PodcastAuthor",
    "Profile",
    "ProfileResult",
    "QuickSearch",
    "Release",
    "Search",
    "SearchResult",
    "SimpleArtist",
    "SimpleBook",
    "SimpleEpisode",
    "SimplePlaylist",
    "SimplePodcast",
    "SimpleProfile",
    "SimpleRelease",
    "SimpleTrack",
    "Stream",
    "StreamUrls",
    "SynthesisPlaylist",
    "Track",
]

# Placeholder for the async client
try:
    from zvuk_music.client_async import ClientAsync

    __all__.append("ClientAsync")
except ImportError:
    pass
