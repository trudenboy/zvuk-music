# Zvuk Music API

Python библиотека для работы с API музыкального сервиса [Zvuk.com](https://zvuk.com) (СберЗвук).

## Установка

```bash
pip install zvuk-music
```

С поддержкой async:

```bash
pip install zvuk-music[async]
```

С ускоренным JSON парсингом:

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

## API Reference

### Client

Основные методы:

| Метод | Описание |
|-------|----------|
| `get_anonymous_token()` | Получить анонимный токен |
| `get_profile()` | Профиль пользователя |
| `quick_search(query)` | Быстрый поиск |
| `search(query)` | Полнотекстовый поиск |
| `get_track(id)` | Получить трек |
| `get_tracks(ids)` | Получить треки |
| `get_stream_url(id, quality)` | URL для стриминга |
| `get_artist(id)` | Получить артиста |
| `get_release(id)` | Получить релиз |
| `get_playlist(id)` | Получить плейлист |
| `create_playlist(name)` | Создать плейлист |
| `like_track(id)` | Лайкнуть трек |
| `get_liked_tracks()` | Лайкнутые треки |

## Лицензия

MIT License
