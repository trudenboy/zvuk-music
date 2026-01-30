# Zvuk Music API

Python-библиотека для работы с API музыкального сервиса [Zvuk.com](https://zvuk.com).

## Установка

```bash
pip install zvuk-music
```

С поддержкой async:

```bash
pip install zvuk-music[async]
```

С ускоренным JSON-парсингом:

```bash
pip install zvuk-music[fast]
```

## Быстрый старт

### Анонимный доступ

```python
from zvuk_music import Client

# Получение анонимного токена (ограниченный функционал)
token = Client.get_anonymous_token()
client = Client(token=token)

# Поиск
results = client.quick_search("Metallica")
for track in results.tracks[:5]:
    print(f"{track.title} - {track.get_artists_str()}")
```

### Авторизованный доступ

Для полного функционала (high quality, лайки, плейлисты) необходим токен авторизованного пользователя:

1. Войдите на [zvuk.com](https://zvuk.com) в браузере
2. Откройте https://zvuk.com/api/tiny/profile
3. Скопируйте значение поля `token`

```python
from zvuk_music import Client

client = Client(token="ваш_токен")

# Получение информации об артисте
artist = client.get_artist(754367, with_popular_tracks=True)
print(f"{artist.title}")
for track in artist.popular_tracks[:5]:
    print(f"  - {track.title}")
```

## Примеры использования

### Поиск

```python
# Быстрый поиск (для автокомплита)
quick = client.quick_search("Nothing Else Matters", limit=5)

# Полнотекстовый поиск
search = client.search("Metallica", limit=10)
print(f"Найдено треков: {search.tracks.page.total}")
print(f"Найдено артистов: {search.artists.page.total}")
```

### Треки

```python
# Получение трека
track = client.get_track(5896627)
print(f"{track.title} ({track.get_duration_str()})")

# Получение URL для стриминга
from zvuk_music import Quality

url = client.get_stream_url(track.id, quality=Quality.HIGH)
print(f"Stream URL: {url}")

# Скачивание трека
track.download("metallica_nothing_else_matters.mp3", quality=Quality.MID)
```

### Плейлисты

```python
# Создание плейлиста
playlist_id = client.create_playlist("Мой плейлист", track_ids=["5896627", "5896628"])

# Добавление треков
client.add_tracks_to_playlist(playlist_id, ["5896629", "5896630"])

# Получение плейлиста
playlist = client.get_playlist(playlist_id)
for track in playlist.tracks:
    print(f"  - {track.title}")

# Удаление плейлиста
client.delete_playlist(playlist_id)
```

### Коллекция (лайки)

```python
# Лайкнуть трек
client.like_track(5896627)

# Получить лайкнутые треки
from zvuk_music import OrderBy, OrderDirection

liked = client.get_liked_tracks(
    order_by=OrderBy.DATE_ADDED,
    direction=OrderDirection.DESC
)
for track in liked[:10]:
    print(f"{track.title} - {track.get_artists_str()}")

# Убрать лайк
client.unlike_track(5896627)
```

### Артисты и релизы

```python
# Информация об артисте
artist = client.get_artist(
    754367,  # Metallica
    with_releases=True,
    with_popular_tracks=True,
    with_related_artists=True,
)

print(f"Артист: {artist.title}")
print(f"Релизов: {len(artist.releases)}")
print(f"Популярные треки: {len(artist.popular_tracks)}")

# Получение релиза
release = client.get_release(artist.releases[0].id)
print(f"\nАльбом: {release.title} ({release.get_year()})")
for track in release.tracks:
    print(f"  {track.position}. {track.title}")
```

## Качество аудио

| Качество | Битрейт | Требует подписку |
|----------|---------|------------------|
| `Quality.MID` | 128kbps MP3 | Нет |
| `Quality.HIGH` | 320kbps MP3 | Да |
| `Quality.FLAC` | FLAC | Да |

```python
from zvuk_music import Quality, SubscriptionRequiredError

try:
    url = client.get_stream_url(track_id, quality=Quality.HIGH)
except SubscriptionRequiredError:
    # Fallback на mid качество
    url = client.get_stream_url(track_id, quality=Quality.MID)
```

## Обработка ошибок

```python
from zvuk_music import (
    ZvukMusicError,
    UnauthorizedError,
    NotFoundError,
    BotDetectedError,
    SubscriptionRequiredError,
)

try:
    track = client.get_track(123456789)
except NotFoundError:
    print("Трек не найден")
except UnauthorizedError:
    print("Невалидный токен")
except BotDetectedError:
    print("API заблокировал запрос (бот-защита)")
except ZvukMusicError as e:
    print(f"Ошибка: {e}")
```

## Асинхронный клиент

```python
import asyncio
from zvuk_music import Client, ClientAsync

async def main():
    token = Client.get_anonymous_token()
    client = ClientAsync(token=token)

    # Параллельные запросы
    track, artist = await asyncio.gather(
        client.get_track(5896627),
        client.get_artist(754367, with_popular_tracks=True),
    )
    print(f"{track.title} — {artist.title}")

asyncio.run(main())
```

Для установки: `pip install zvuk-music[async]`

## CLI

Скрипт `scripts/zvuk_cli.py` предоставляет доступ ко всем 58 методам API через командную строку. Вывод в формате JSON.

### Запуск

```bash
python scripts/zvuk_cli.py <субкоманда> [аргументы]
```

### Глобальные флаги

| Флаг | Описание |
|------|----------|
| `-t`, `--token` | Токен авторизации (также читается из `ZVUK_TOKEN`) |
| `-p`, `--pretty` | Форматировать JSON с отступами (indent=2) |
| `--timeout` | Таймаут запросов в секундах (по умолчанию 10) |
| `--proxy` | URL прокси-сервера |

### Примеры

```bash
# Получить анонимный токен
python scripts/zvuk_cli.py get-anonymous-token

# Поиск (с форматированным выводом)
python scripts/zvuk_cli.py -p quick-search "Metallica" --limit 3

# Получить трек
python scripts/zvuk_cli.py -p track-get 5896627

# Информация об артисте с релизами
python scripts/zvuk_cli.py -p artist-get 754367 --with-releases --releases-limit 5

# Использование токена через переменную окружения
export ZVUK_TOKEN=<ваш_токен>
python scripts/zvuk_cli.py -p collection-liked-tracks --order-by dateAdded
python scripts/zvuk_cli.py -p like-track 5896627

# Создание плейлиста
python scripts/zvuk_cli.py -p playlist-create "Мой плейлист" --track-ids 5896627 5896628

# Полнотекстовый поиск без подкастов и книг
python scripts/zvuk_cli.py -p search "Nothing Else Matters" --no-podcasts --no-books
```

### Все субкоманды

**Авторизация:**
`get-anonymous-token`, `init`, `get-profile`, `is-authorized`

**Поиск:**
`quick-search`, `search`

**Треки:**
`track-get`, `tracks-get`, `track-get-full`, `stream-url`, `stream-urls`

**Релизы:**
`release-get`, `releases-get`

**Артисты:**
`artist-get`, `artists-get`

**Плейлисты:**
`playlist-get`, `playlists-get`, `playlist-get-short`, `playlist-tracks`,
`playlist-create`, `playlist-delete`, `playlist-rename`, `playlist-add-tracks`,
`playlist-update`, `playlist-set-public`, `synthesis-playlist-build`, `synthesis-playlists-get`

**Подкасты:**
`podcast-get`, `podcasts-get`, `episode-get`, `episodes-get`

**Коллекция:**
`collection-get`, `collection-liked-tracks`, `collection-playlists`, `collection-podcasts`,
`collection-add`, `collection-remove`,
`like-track`, `unlike-track`, `like-release`, `unlike-release`,
`like-artist`, `unlike-artist`, `like-playlist`, `unlike-playlist`,
`like-podcast`, `unlike-podcast`

**Скрытые:**
`hidden-collection`, `hidden-tracks`, `hidden-add`, `hidden-remove`,
`hide-track`, `unhide-track`

**Профили:**
`profile-followers-count`, `profile-following-count`

**История:**
`listening-history`, `listened-episodes`, `has-unread-notifications`

Справка по любой субкоманде: `python scripts/zvuk_cli.py <субкоманда> --help`

## Справочник API

### Client

58 методов. Все методы доступны как в синхронном (`Client`), так и в асинхронном (`ClientAsync`) клиентах.

**Авторизация и профиль:**

| Метод | Описание |
|-------|----------|
| `get_anonymous_token()` | Получить анонимный токен |
| `init()` | Инициализация клиента (загрузка профиля) |
| `get_profile()` | Профиль пользователя |
| `is_authorized()` | Проверка авторизации |

**Поиск:**

| Метод | Описание |
|-------|----------|
| `quick_search(query)` | Быстрый поиск (автокомплит) |
| `search(query)` | Полнотекстовый поиск |

**Треки и стриминг:**

| Метод | Описание |
|-------|----------|
| `get_track(id)` | Получить трек |
| `get_tracks(ids)` | Получить несколько треков |
| `get_full_track(id)` | Трек с артистами и релизами |
| `get_stream_url(id, quality)` | URL для стриминга |
| `get_stream_urls(ids)` | Несколько URL стримов |

**Артисты и релизы:**

| Метод | Описание |
|-------|----------|
| `get_artist(id)` | Артист (с релизами, треками, связанными) |
| `get_artists(ids)` | Несколько артистов |
| `get_release(id)` | Релиз (альбом/сингл) |
| `get_releases(ids)` | Несколько релизов |

**Плейлисты:**

| Метод | Описание |
|-------|----------|
| `get_playlist(id)` | Получить плейлист |
| `get_playlists(ids)` | Несколько плейлистов |
| `get_playlist_tracks(id)` | Треки плейлиста |
| `create_playlist(name)` | Создать плейлист |
| `rename_playlist(id, name)` | Переименовать |
| `add_tracks_to_playlist(id, track_ids)` | Добавить треки |
| `update_playlist(id, track_ids)` | Обновить плейлист |
| `set_playlist_public(id, is_public)` | Изменить видимость |
| `delete_playlist(id)` | Удалить плейлист |

**Подкасты:**

| Метод | Описание |
|-------|----------|
| `get_podcast(id)` | Получить подкаст |
| `get_podcasts(ids)` | Несколько подкастов |
| `get_episode(id)` | Получить эпизод |
| `get_episodes(ids)` | Несколько эпизодов |

**Коллекция (лайки):**

| Метод | Описание |
|-------|----------|
| `get_collection()` | Коллекция пользователя |
| `get_liked_tracks()` | Лайкнутые треки |
| `get_user_playlists()` | Плейлисты пользователя |
| `like_track(id)` / `unlike_track(id)` | Лайк / анлайк трека |
| `like_release(id)` / `unlike_release(id)` | Лайк / анлайк релиза |
| `like_artist(id)` / `unlike_artist(id)` | Лайк / анлайк артиста |
| `like_playlist(id)` / `unlike_playlist(id)` | Лайк / анлайк плейлиста |
| `like_podcast(id)` / `unlike_podcast(id)` | Лайк / анлайк подкаста |

**Скрытая коллекция:**

| Метод | Описание |
|-------|----------|
| `get_hidden_collection()` | Скрытые элементы |
| `get_hidden_tracks()` | Скрытые треки |
| `hide_track(id)` / `unhide_track(id)` | Скрыть / показать трек |

**Профили и социальные функции:**

| Метод | Описание |
|-------|----------|
| `get_profile_followers_count(ids)` | Количество подписчиков |
| `get_following_count(id)` | Количество подписок |
| `has_unread_notifications()` | Непрочитанные уведомления |

## Лицензия

MIT License
