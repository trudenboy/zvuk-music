"""Модели данных Zvuk Music API."""

from zvuk_music.models.artist import Artist, SimpleArtist
from zvuk_music.models.book import BookAuthor, SimpleBook
from zvuk_music.models.collection import Collection, CollectionItem, HiddenCollection
from zvuk_music.models.common import Animation, Background, Genre, Image, Label
from zvuk_music.models.playlist import (
    Playlist,
    PlaylistAuthor,
    PlaylistItem,
    SimplePlaylist,
    SynthesisPlaylist,
)
from zvuk_music.models.podcast import (
    Episode,
    Podcast,
    PodcastAuthor,
    SimpleEpisode,
    SimplePodcast,
)
from zvuk_music.models.profile import ExternalProfile, Profile, ProfileResult, SimpleProfile
from zvuk_music.models.release import Release, SimpleRelease
from zvuk_music.models.search import Page, QuickSearch, Search, SearchResult
from zvuk_music.models.stream import Stream, StreamUrls
from zvuk_music.models.track import SimpleTrack, Track

__all__ = [
    # common
    "Animation",
    "Background",
    "Genre",
    "Image",
    "Label",
    # artist
    "Artist",
    "SimpleArtist",
    # track
    "Track",
    "SimpleTrack",
    # release
    "Release",
    "SimpleRelease",
    # stream
    "Stream",
    "StreamUrls",
    # playlist
    "Playlist",
    "PlaylistAuthor",
    "PlaylistItem",
    "SimplePlaylist",
    "SynthesisPlaylist",
    # podcast
    "Episode",
    "Podcast",
    "PodcastAuthor",
    "SimpleEpisode",
    "SimplePodcast",
    # collection
    "Collection",
    "CollectionItem",
    "HiddenCollection",
    # profile
    "ExternalProfile",
    "Profile",
    "ProfileResult",
    "SimpleProfile",
    # search
    "Page",
    "QuickSearch",
    "Search",
    "SearchResult",
    # book
    "BookAuthor",
    "SimpleBook",
]
