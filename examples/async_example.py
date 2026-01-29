"""Пример использования асинхронного клиента."""

import asyncio

from zvuk_music import Client, ClientAsync


async def main() -> None:
    # Получаем анонимный токен (синхронный метод)
    print("=== Получение токена ===")
    token = Client.get_anonymous_token()
    print(f"Токен: {token[:20]}...")

    # Создаём async клиент
    client = ClientAsync(token=token)

    # Быстрый поиск
    print("\n=== Async быстрый поиск 'Metallica' ===")
    results = await client.quick_search("Metallica", limit=5)

    print(f"Найдено треков: {len(results.tracks)}")
    for track in results.tracks:
        print(f"  - {track.title} - {track.get_artists_str()}")

    print(f"Найдено артистов: {len(results.artists)}")
    for artist in results.artists:
        print(f"  - {artist.title}")

    # Получение нескольких треков параллельно
    print("\n=== Параллельное получение данных ===")

    # Запускаем несколько запросов параллельно
    track_task = client.get_track(5896627)
    artist_task = client.get_artist(754367, with_popular_tracks=True, tracks_limit=3)
    search_task = client.search("Nothing Else Matters", limit=3)

    track, artist, search = await asyncio.gather(track_task, artist_task, search_task)

    print(f"\nТрек: {track.title if track else 'N/A'}")
    print(f"Артист: {artist.title if artist else 'N/A'}")
    if artist:
        print(f"  Популярных треков: {len(artist.popular_tracks)}")
    if search and search.tracks:
        print(f"Найдено в поиске: {len(search.tracks.items)} треков")

    # Получение стрима
    print("\n=== Получение URL стрима ===")
    streams = await client.get_stream_urls([5896627, 5896623])
    print(f"Получено {len(streams)} стримов")
    for stream in streams:
        print(f"  Mid URL доступен: {'да' if stream.mid else 'нет'}")

    print("\n=== Async тесты завершены ===")


if __name__ == "__main__":
    asyncio.run(main())
