#!/usr/bin/env python3
"""CLI для Zvuk Music API.

Оборачивает все 58 методов Client в argparse-субкоманды.
Вывод в JSON (compact по умолчанию, --pretty для indent=2).

Использование:
    python scripts/zvuk_cli.py --help
    python scripts/zvuk_cli.py -p track-get 5896627
    python scripts/zvuk_cli.py -p quick-search "Metallica" --limit 3

    export ZVUK_TOKEN=<token>
    python scripts/zvuk_cli.py -p like-track 5896627
"""

import argparse
import json
import os
import sys
from typing import Any, Callable, Dict, List, Optional, Sequence

from zvuk_music.base import ZvukMusicModel
from zvuk_music.client import Client
from zvuk_music.enums import CollectionItemType, OrderBy, OrderDirection, Quality
from zvuk_music.exceptions import ZvukMusicError

# ========== Helpers ==========


def serialize_result(obj: Any) -> Any:
    """Сериализует результат в JSON-совместимый объект."""
    if obj is None:
        return None
    if isinstance(obj, ZvukMusicModel):
        return obj.to_dict()
    if isinstance(obj, list):
        return [serialize_result(item) for item in obj]
    if isinstance(obj, dict):
        return {k: serialize_result(v) for k, v in obj.items()}
    if isinstance(obj, (str, int, float, bool)):
        return obj
    return str(obj)


def print_result(result: Any, pretty: bool = False) -> None:
    """Выводит результат в JSON на stdout."""
    data = serialize_result(result)
    indent = 2 if pretty else None
    print(json.dumps(data, ensure_ascii=False, indent=indent))


def error_exit(message: str, code: int = 1) -> None:
    """Выводит ошибку в JSON на stderr и завершает процесс."""
    print(json.dumps({"error": message}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


def make_client(args: argparse.Namespace) -> Client:
    """Создаёт Client из аргументов CLI."""
    token = args.token or os.environ.get("ZVUK_TOKEN")
    return Client(
        token=token,
        timeout=args.timeout,
        proxy_url=args.proxy,
    )


# ========== Handler factories ==========

HandlerFunc = Callable[[Client, argparse.Namespace], Any]


def _no_arg(method_name: str) -> HandlerFunc:
    """Фабрика хендлеров для методов без аргументов."""

    def handler(client: Client, args: argparse.Namespace) -> Any:
        return getattr(client, method_name)()

    return handler


def _single_id(method_name: str, id_arg: str) -> HandlerFunc:
    """Фабрика хендлеров для методов с одним ID."""

    def handler(client: Client, args: argparse.Namespace) -> Any:
        return getattr(client, method_name)(getattr(args, id_arg))

    return handler


def _multi_id(method_name: str, id_arg: str) -> HandlerFunc:
    """Фабрика хендлеров для методов со списком ID."""

    def handler(client: Client, args: argparse.Namespace) -> Any:
        return getattr(client, method_name)(getattr(args, id_arg))

    return handler


def _like(method_name: str, id_arg: str) -> HandlerFunc:
    """Фабрика хендлеров для like/unlike методов."""

    def handler(client: Client, args: argparse.Namespace) -> Any:
        result = getattr(client, method_name)(getattr(args, id_arg))
        return {"success": result}

    return handler


# ========== Explicit handlers ==========


def handle_get_anonymous_token(client: Client, args: argparse.Namespace) -> Any:
    token = Client.get_anonymous_token()
    return {"token": token}


def handle_init(client: Client, args: argparse.Namespace) -> Any:
    client.init()
    return {
        "authorized": client.is_authorized(),
        "profile_id": str(client._profile.id) if client._profile else None,
    }


def handle_is_authorized(client: Client, args: argparse.Namespace) -> Any:
    client.init()
    return {"authorized": client.is_authorized()}


def handle_quick_search(client: Client, args: argparse.Namespace) -> Any:
    return client.quick_search(
        query=args.query,
        limit=args.limit,
        search_session_id=args.search_session_id,
    )


def handle_search(client: Client, args: argparse.Namespace) -> Any:
    return client.search(
        query=args.query,
        limit=args.limit,
        tracks=not args.no_tracks,
        artists=not args.no_artists,
        releases=not args.no_releases,
        playlists=not args.no_playlists,
        podcasts=not args.no_podcasts,
        episodes=not args.no_episodes,
        profiles=not args.no_profiles,
        books=not args.no_books,
        track_cursor=args.track_cursor,
        artist_cursor=args.artist_cursor,
        release_cursor=args.release_cursor,
        playlist_cursor=args.playlist_cursor,
    )


def handle_track_get_full(client: Client, args: argparse.Namespace) -> Any:
    return client.get_full_track(
        track_ids=args.track_ids,
        with_artists=args.with_artists,
        with_releases=args.with_releases,
    )


def handle_stream_url(client: Client, args: argparse.Namespace) -> Any:
    quality = Quality(args.quality)
    url = client.get_stream_url(args.track_id, quality=quality)
    return {"url": url}


def handle_releases_get(client: Client, args: argparse.Namespace) -> Any:
    return client.get_releases(args.release_ids, related_limit=args.related_limit)


def handle_artist_get(client: Client, args: argparse.Namespace) -> Any:
    return client.get_artist(
        args.artist_id,
        with_releases=args.with_releases,
        releases_limit=args.releases_limit,
        releases_offset=args.releases_offset,
        with_popular_tracks=args.with_popular_tracks,
        tracks_limit=args.tracks_limit,
        tracks_offset=args.tracks_offset,
        with_related_artists=args.with_related_artists,
        related_artists_limit=args.related_artists_limit,
        with_description=args.with_description,
    )


def handle_artists_get(client: Client, args: argparse.Namespace) -> Any:
    return client.get_artists(
        args.ids,
        with_releases=args.with_releases,
        releases_limit=args.releases_limit,
        releases_offset=args.releases_offset,
        with_popular_tracks=args.with_popular_tracks,
        tracks_limit=args.tracks_limit,
        tracks_offset=args.tracks_offset,
        with_related_artists=args.with_related_artists,
        related_artists_limit=args.related_artists_limit,
        with_description=args.with_description,
    )


def handle_playlist_tracks(client: Client, args: argparse.Namespace) -> Any:
    return client.get_playlist_tracks(
        args.playlist_id,
        limit=args.limit,
        offset=args.offset,
    )


def handle_playlist_create(client: Client, args: argparse.Namespace) -> Any:
    playlist_id = client.create_playlist(args.name, track_ids=args.track_ids)
    return {"playlist_id": playlist_id}


def handle_playlist_delete(client: Client, args: argparse.Namespace) -> Any:
    result = client.delete_playlist(args.playlist_id)
    return {"success": result}


def handle_playlist_rename(client: Client, args: argparse.Namespace) -> Any:
    result = client.rename_playlist(args.playlist_id, args.new_name)
    return {"success": result}


def handle_playlist_add_tracks(client: Client, args: argparse.Namespace) -> Any:
    result = client.add_tracks_to_playlist(args.playlist_id, args.track_ids)
    return {"success": result}


def handle_playlist_update(client: Client, args: argparse.Namespace) -> Any:
    is_public: Optional[bool] = None
    if args.public:
        is_public = True
    elif args.private:
        is_public = False

    result = client.update_playlist(
        args.playlist_id,
        track_ids=args.track_ids,
        name=args.name,
        is_public=is_public,
    )
    return {"success": result}


def handle_playlist_set_public(client: Client, args: argparse.Namespace) -> Any:
    if args.public:
        is_public = True
    elif args.private:
        is_public = False
    else:
        error_exit("Укажите --public или --private")
        return None  # unreachable
    result = client.set_playlist_public(args.playlist_id, is_public)
    return {"success": result}


def handle_synthesis_playlist_build(client: Client, args: argparse.Namespace) -> Any:
    return client.synthesis_playlist_build(args.first_author_id, args.second_author_id)


def handle_collection_liked_tracks(client: Client, args: argparse.Namespace) -> Any:
    order_by = OrderBy(args.order_by)
    direction = OrderDirection(args.direction)
    return client.get_liked_tracks(order_by=order_by, direction=direction)


def handle_collection_podcasts(client: Client, args: argparse.Namespace) -> Any:
    return client.get_user_paginated_podcasts(cursor=args.cursor, count=args.count)


def handle_collection_add(client: Client, args: argparse.Namespace) -> Any:
    item_type = CollectionItemType(args.type)
    result = client.add_to_collection(args.item_id, item_type)
    return {"success": result}


def handle_collection_remove(client: Client, args: argparse.Namespace) -> Any:
    item_type = CollectionItemType(args.type)
    result = client.remove_from_collection(args.item_id, item_type)
    return {"success": result}


def handle_hidden_add(client: Client, args: argparse.Namespace) -> Any:
    item_type = CollectionItemType(args.type)
    result = client.add_to_hidden(args.item_id, item_type)
    return {"success": result}


def handle_hidden_remove(client: Client, args: argparse.Namespace) -> Any:
    item_type = CollectionItemType(args.type)
    result = client.remove_from_hidden(args.item_id, item_type)
    return {"success": result}


def handle_profile_following_count(client: Client, args: argparse.Namespace) -> Any:
    count = client.get_following_count(args.profile_id)
    return {"count": count}


def handle_profile_followers_count(client: Client, args: argparse.Namespace) -> Any:
    counts = client.get_profile_followers_count(args.ids)
    return {"ids": args.ids, "counts": counts}


# ========== Argument definitions ==========

# Reusable argument specs
_ARTIST_FLAGS: List[Dict[str, Any]] = [
    {"flags": ["--with-releases"], "action": "store_true", "help": "Включить релизы"},
    {"flags": ["--releases-limit"], "type": int, "default": 100, "help": "Лимит релизов"},
    {"flags": ["--releases-offset"], "type": int, "default": 0, "help": "Смещение релизов"},
    {
        "flags": ["--with-popular-tracks"],
        "action": "store_true",
        "help": "Включить популярные треки",
    },
    {"flags": ["--tracks-limit"], "type": int, "default": 100, "help": "Лимит треков"},
    {"flags": ["--tracks-offset"], "type": int, "default": 0, "help": "Смещение треков"},
    {
        "flags": ["--with-related-artists"],
        "action": "store_true",
        "help": "Включить похожих артистов",
    },
    {
        "flags": ["--related-artists-limit"],
        "type": int,
        "default": 100,
        "help": "Лимит похожих артистов",
    },
    {"flags": ["--with-description"], "action": "store_true", "help": "Включить описание"},
]

_COLLECTION_TYPE_CHOICES = [t.value for t in CollectionItemType]

# ========== COMMANDS table ==========

CommandDef = Dict[str, Any]

COMMANDS: List[CommandDef] = [
    # === Auth ===
    {
        "name": "get-anonymous-token",
        "help": "Получить анонимный токен",
        "args": [],
        "handler": handle_get_anonymous_token,
    },
    {
        "name": "init",
        "help": "Инициализировать клиент, загрузить профиль",
        "args": [],
        "handler": handle_init,
    },
    {
        "name": "get-profile",
        "help": "Получить профиль текущего пользователя",
        "args": [],
        "handler": _no_arg("get_profile"),
    },
    {
        "name": "is-authorized",
        "help": "Проверить авторизацию",
        "args": [],
        "handler": handle_is_authorized,
    },
    # === Search ===
    {
        "name": "quick-search",
        "help": "Быстрый поиск с автодополнением",
        "args": [
            {"flags": ["query"], "help": "Поисковый запрос"},
            {"flags": ["--limit"], "type": int, "default": 10, "help": "Максимум результатов"},
            {"flags": ["--search-session-id"], "help": "ID сессии поиска"},
        ],
        "handler": handle_quick_search,
    },
    {
        "name": "search",
        "help": "Полнотекстовый поиск",
        "args": [
            {"flags": ["query"], "help": "Поисковый запрос"},
            {
                "flags": ["--limit"],
                "type": int,
                "default": 20,
                "help": "Максимум результатов в категории",
            },
            {"flags": ["--no-tracks"], "action": "store_true", "help": "Не искать треки"},
            {"flags": ["--no-artists"], "action": "store_true", "help": "Не искать артистов"},
            {"flags": ["--no-releases"], "action": "store_true", "help": "Не искать релизы"},
            {"flags": ["--no-playlists"], "action": "store_true", "help": "Не искать плейлисты"},
            {"flags": ["--no-podcasts"], "action": "store_true", "help": "Не искать подкасты"},
            {"flags": ["--no-episodes"], "action": "store_true", "help": "Не искать эпизоды"},
            {"flags": ["--no-profiles"], "action": "store_true", "help": "Не искать профили"},
            {"flags": ["--no-books"], "action": "store_true", "help": "Не искать книги"},
            {"flags": ["--track-cursor"], "help": "Курсор для треков"},
            {"flags": ["--artist-cursor"], "help": "Курсор для артистов"},
            {"flags": ["--release-cursor"], "help": "Курсор для релизов"},
            {"flags": ["--playlist-cursor"], "help": "Курсор для плейлистов"},
        ],
        "handler": handle_search,
    },
    # === Tracks ===
    {
        "name": "track-get",
        "help": "Получить трек по ID",
        "args": [{"flags": ["track_id"], "help": "ID трека"}],
        "handler": _single_id("get_track", "track_id"),
    },
    {
        "name": "tracks-get",
        "help": "Получить треки по ID",
        "args": [{"flags": ["track_ids"], "nargs": "+", "help": "ID треков"}],
        "handler": _multi_id("get_tracks", "track_ids"),
    },
    {
        "name": "track-get-full",
        "help": "Получить полную информацию о треках",
        "args": [
            {"flags": ["track_ids"], "nargs": "+", "help": "ID треков"},
            {
                "flags": ["--with-artists"],
                "action": "store_true",
                "help": "Включить информацию об артистах",
            },
            {
                "flags": ["--with-releases"],
                "action": "store_true",
                "help": "Включить информацию о релизах",
            },
        ],
        "handler": handle_track_get_full,
    },
    {
        "name": "stream-url",
        "help": "Получить URL для стриминга",
        "args": [
            {"flags": ["track_id"], "help": "ID трека"},
            {
                "flags": ["--quality"],
                "choices": ["mid", "high", "flacdrm"],
                "default": "high",
                "help": "Качество аудио (default: high)",
            },
        ],
        "handler": handle_stream_url,
    },
    {
        "name": "stream-urls",
        "help": "Получить URL для стриминга (несколько треков)",
        "args": [{"flags": ["track_ids"], "nargs": "+", "help": "ID треков"}],
        "handler": _multi_id("get_stream_urls", "track_ids"),
    },
    # === Releases ===
    {
        "name": "release-get",
        "help": "Получить релиз по ID",
        "args": [{"flags": ["release_id"], "help": "ID релиза"}],
        "handler": _single_id("get_release", "release_id"),
    },
    {
        "name": "releases-get",
        "help": "Получить релизы по ID",
        "args": [
            {"flags": ["release_ids"], "nargs": "+", "help": "ID релизов"},
            {
                "flags": ["--related-limit"],
                "type": int,
                "default": 10,
                "help": "Количество похожих релизов",
            },
        ],
        "handler": handle_releases_get,
    },
    # === Artists ===
    {
        "name": "artist-get",
        "help": "Получить артиста по ID",
        "args": [{"flags": ["artist_id"], "help": "ID артиста"}] + _ARTIST_FLAGS,
        "handler": handle_artist_get,
    },
    {
        "name": "artists-get",
        "help": "Получить артистов по ID",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID артистов"}] + _ARTIST_FLAGS,
        "handler": handle_artists_get,
    },
    # === Playlists ===
    {
        "name": "playlist-get",
        "help": "Получить плейлист по ID",
        "args": [{"flags": ["playlist_id"], "help": "ID плейлиста"}],
        "handler": _single_id("get_playlist", "playlist_id"),
    },
    {
        "name": "playlists-get",
        "help": "Получить плейлисты по ID",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID плейлистов"}],
        "handler": _multi_id("get_playlists", "ids"),
    },
    {
        "name": "playlist-get-short",
        "help": "Получить краткую информацию о плейлистах",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID плейлистов"}],
        "handler": _multi_id("get_short_playlist", "ids"),
    },
    {
        "name": "playlist-tracks",
        "help": "Получить треки плейлиста",
        "args": [
            {"flags": ["playlist_id"], "help": "ID плейлиста"},
            {"flags": ["--limit"], "type": int, "default": 50, "help": "Количество треков"},
            {"flags": ["--offset"], "type": int, "default": 0, "help": "Смещение"},
        ],
        "handler": handle_playlist_tracks,
    },
    {
        "name": "playlist-create",
        "help": "Создать плейлист",
        "args": [
            {"flags": ["name"], "help": "Название плейлиста"},
            {"flags": ["--track-ids"], "nargs": "+", "help": "ID треков для добавления"},
        ],
        "handler": handle_playlist_create,
    },
    {
        "name": "playlist-delete",
        "help": "Удалить плейлист",
        "args": [{"flags": ["playlist_id"], "help": "ID плейлиста"}],
        "handler": handle_playlist_delete,
    },
    {
        "name": "playlist-rename",
        "help": "Переименовать плейлист",
        "args": [
            {"flags": ["playlist_id"], "help": "ID плейлиста"},
            {"flags": ["new_name"], "help": "Новое название"},
        ],
        "handler": handle_playlist_rename,
    },
    {
        "name": "playlist-add-tracks",
        "help": "Добавить треки в плейлист",
        "args": [
            {"flags": ["playlist_id"], "help": "ID плейлиста"},
            {
                "flags": ["--track-ids"],
                "nargs": "+",
                "required": True,
                "help": "ID треков",
            },
        ],
        "handler": handle_playlist_add_tracks,
    },
    {
        "name": "playlist-update",
        "help": "Обновить плейлист целиком",
        "args": [
            {"flags": ["playlist_id"], "help": "ID плейлиста"},
            {
                "flags": ["--track-ids"],
                "nargs": "+",
                "required": True,
                "help": "Новый список треков",
            },
            {"flags": ["--name"], "help": "Новое название"},
            {"flags": ["--public"], "action": "store_true", "help": "Сделать публичным"},
            {"flags": ["--private"], "action": "store_true", "help": "Сделать приватным"},
        ],
        "handler": handle_playlist_update,
    },
    {
        "name": "playlist-set-public",
        "help": "Изменить видимость плейлиста",
        "args": [
            {"flags": ["playlist_id"], "help": "ID плейлиста"},
        ],
        "handler": handle_playlist_set_public,
        "mutually_exclusive": [
            {"flags": ["--public"], "action": "store_true", "help": "Сделать публичным"},
            {"flags": ["--private"], "action": "store_true", "help": "Сделать приватным"},
        ],
    },
    {
        "name": "synthesis-playlist-build",
        "help": "Создать синтез-плейлист",
        "args": [
            {"flags": ["first_author_id"], "help": "ID первого автора"},
            {"flags": ["second_author_id"], "help": "ID второго автора"},
        ],
        "handler": handle_synthesis_playlist_build,
    },
    {
        "name": "synthesis-playlists-get",
        "help": "Получить синтез-плейлисты",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID плейлистов"}],
        "handler": _multi_id("get_synthesis_playlists", "ids"),
    },
    # === Podcasts ===
    {
        "name": "podcast-get",
        "help": "Получить подкаст по ID",
        "args": [{"flags": ["podcast_id"], "help": "ID подкаста"}],
        "handler": _single_id("get_podcast", "podcast_id"),
    },
    {
        "name": "podcasts-get",
        "help": "Получить подкасты по ID",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID подкастов"}],
        "handler": _multi_id("get_podcasts", "ids"),
    },
    {
        "name": "episode-get",
        "help": "Получить эпизод по ID",
        "args": [{"flags": ["episode_id"], "help": "ID эпизода"}],
        "handler": _single_id("get_episode", "episode_id"),
    },
    {
        "name": "episodes-get",
        "help": "Получить эпизоды по ID",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID эпизодов"}],
        "handler": _multi_id("get_episodes", "ids"),
    },
    # === Collection ===
    {
        "name": "collection-get",
        "help": "Получить коллекцию пользователя",
        "args": [],
        "handler": _no_arg("get_collection"),
    },
    {
        "name": "collection-liked-tracks",
        "help": "Получить лайкнутые треки",
        "args": [
            {
                "flags": ["--order-by"],
                "choices": ["alphabet", "artist", "dateAdded"],
                "default": "dateAdded",
                "help": "Сортировка (default: dateAdded)",
            },
            {
                "flags": ["--direction"],
                "choices": ["asc", "desc"],
                "default": "desc",
                "help": "Направление сортировки (default: desc)",
            },
        ],
        "handler": handle_collection_liked_tracks,
    },
    {
        "name": "collection-playlists",
        "help": "Получить плейлисты пользователя",
        "args": [],
        "handler": _no_arg("get_user_playlists"),
    },
    {
        "name": "collection-podcasts",
        "help": "Получить подкасты пользователя",
        "args": [
            {"flags": ["--cursor"], "help": "Курсор для пагинации"},
            {"flags": ["--count"], "type": int, "default": 20, "help": "Количество подкастов"},
        ],
        "handler": handle_collection_podcasts,
    },
    {
        "name": "collection-add",
        "help": "Добавить элемент в коллекцию (лайк)",
        "args": [
            {"flags": ["item_id"], "help": "ID элемента"},
            {
                "flags": ["--type"],
                "required": True,
                "choices": _COLLECTION_TYPE_CHOICES,
                "help": "Тип элемента",
                "dest": "type",
            },
        ],
        "handler": handle_collection_add,
    },
    {
        "name": "collection-remove",
        "help": "Убрать элемент из коллекции",
        "args": [
            {"flags": ["item_id"], "help": "ID элемента"},
            {
                "flags": ["--type"],
                "required": True,
                "choices": _COLLECTION_TYPE_CHOICES,
                "help": "Тип элемента",
                "dest": "type",
            },
        ],
        "handler": handle_collection_remove,
    },
    # Like/unlike shortcuts
    {
        "name": "like-track",
        "help": "Лайкнуть трек",
        "args": [{"flags": ["track_id"], "help": "ID трека"}],
        "handler": _like("like_track", "track_id"),
    },
    {
        "name": "unlike-track",
        "help": "Убрать лайк с трека",
        "args": [{"flags": ["track_id"], "help": "ID трека"}],
        "handler": _like("unlike_track", "track_id"),
    },
    {
        "name": "like-release",
        "help": "Лайкнуть релиз",
        "args": [{"flags": ["release_id"], "help": "ID релиза"}],
        "handler": _like("like_release", "release_id"),
    },
    {
        "name": "unlike-release",
        "help": "Убрать лайк с релиза",
        "args": [{"flags": ["release_id"], "help": "ID релиза"}],
        "handler": _like("unlike_release", "release_id"),
    },
    {
        "name": "like-artist",
        "help": "Лайкнуть артиста",
        "args": [{"flags": ["artist_id"], "help": "ID артиста"}],
        "handler": _like("like_artist", "artist_id"),
    },
    {
        "name": "unlike-artist",
        "help": "Убрать лайк с артиста",
        "args": [{"flags": ["artist_id"], "help": "ID артиста"}],
        "handler": _like("unlike_artist", "artist_id"),
    },
    {
        "name": "like-playlist",
        "help": "Лайкнуть плейлист",
        "args": [{"flags": ["playlist_id"], "help": "ID плейлиста"}],
        "handler": _like("like_playlist", "playlist_id"),
    },
    {
        "name": "unlike-playlist",
        "help": "Убрать лайк с плейлиста",
        "args": [{"flags": ["playlist_id"], "help": "ID плейлиста"}],
        "handler": _like("unlike_playlist", "playlist_id"),
    },
    {
        "name": "like-podcast",
        "help": "Лайкнуть подкаст",
        "args": [{"flags": ["podcast_id"], "help": "ID подкаста"}],
        "handler": _like("like_podcast", "podcast_id"),
    },
    {
        "name": "unlike-podcast",
        "help": "Убрать лайк с подкаста",
        "args": [{"flags": ["podcast_id"], "help": "ID подкаста"}],
        "handler": _like("unlike_podcast", "podcast_id"),
    },
    # === Hidden ===
    {
        "name": "hidden-collection",
        "help": "Получить скрытые элементы",
        "args": [],
        "handler": _no_arg("get_hidden_collection"),
    },
    {
        "name": "hidden-tracks",
        "help": "Получить скрытые треки",
        "args": [],
        "handler": _no_arg("get_hidden_tracks"),
    },
    {
        "name": "hidden-add",
        "help": "Скрыть элемент",
        "args": [
            {"flags": ["item_id"], "help": "ID элемента"},
            {
                "flags": ["--type"],
                "required": True,
                "choices": _COLLECTION_TYPE_CHOICES,
                "help": "Тип элемента",
                "dest": "type",
            },
        ],
        "handler": handle_hidden_add,
    },
    {
        "name": "hidden-remove",
        "help": "Убрать элемент из скрытых",
        "args": [
            {"flags": ["item_id"], "help": "ID элемента"},
            {
                "flags": ["--type"],
                "required": True,
                "choices": _COLLECTION_TYPE_CHOICES,
                "help": "Тип элемента",
                "dest": "type",
            },
        ],
        "handler": handle_hidden_remove,
    },
    {
        "name": "hide-track",
        "help": "Скрыть трек",
        "args": [{"flags": ["track_id"], "help": "ID трека"}],
        "handler": _like("hide_track", "track_id"),
    },
    {
        "name": "unhide-track",
        "help": "Убрать трек из скрытых",
        "args": [{"flags": ["track_id"], "help": "ID трека"}],
        "handler": _like("unhide_track", "track_id"),
    },
    # === Profiles ===
    {
        "name": "profile-followers-count",
        "help": "Получить количество подписчиков",
        "args": [{"flags": ["ids"], "nargs": "+", "help": "ID профилей"}],
        "handler": handle_profile_followers_count,
    },
    {
        "name": "profile-following-count",
        "help": "Получить количество подписок",
        "args": [{"flags": ["profile_id"], "help": "ID профиля"}],
        "handler": handle_profile_following_count,
    },
    # === History ===
    {
        "name": "listening-history",
        "help": "Получить историю прослушивания",
        "args": [],
        "handler": _no_arg("get_listening_history"),
    },
    {
        "name": "listened-episodes",
        "help": "Получить прослушанные эпизоды",
        "args": [],
        "handler": _no_arg("get_listened_episodes"),
    },
    {
        "name": "has-unread-notifications",
        "help": "Проверить непрочитанные уведомления",
        "args": [],
        "handler": lambda c, _a: {"has_unread": c.has_unread_notifications()},
    },
]


# ========== Parser builder ==========


def _add_arg(
    parser: "argparse.ArgumentParser | argparse._MutuallyExclusiveGroup",
    arg_def: Dict[str, Any],
) -> None:
    """Добавляет аргумент в парсер из определения."""
    spec = arg_def.copy()
    flags = spec.pop("flags")
    parser.add_argument(*flags, **spec)


def build_parser() -> argparse.ArgumentParser:
    """Строит argparse из COMMANDS."""
    parser = argparse.ArgumentParser(
        prog="zvuk_cli",
        description="CLI for Zvuk Music API",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="Токен авторизации (или env ZVUK_TOKEN)",
    )
    parser.add_argument(
        "-p",
        "--pretty",
        action="store_true",
        help="Форматировать JSON (indent=2)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Таймаут запросов в секундах (default: 10)",
    )
    parser.add_argument(
        "--proxy",
        help="URL прокси сервера",
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    for cmd in COMMANDS:
        sub = subparsers.add_parser(cmd["name"], help=cmd["help"])

        for arg_def in cmd.get("args", []):
            _add_arg(sub, arg_def)

        # Mutually exclusive groups
        if "mutually_exclusive" in cmd:
            group = sub.add_mutually_exclusive_group()
            for arg_def in cmd["mutually_exclusive"]:
                _add_arg(group, arg_def)

        sub.set_defaults(handler=cmd["handler"])

    return parser


# ========== Entry point ==========


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Entry point CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(2)

    try:
        client = make_client(args)
        result = args.handler(client, args)
        print_result(result, pretty=args.pretty)
    except ZvukMusicError as e:
        error_exit(str(e), code=1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
