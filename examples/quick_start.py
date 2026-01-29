"""Пример быстрого старта с Zvuk Music API."""

from zvuk_music import Client, Quality


def main() -> None:
    # Получение анонимного токена
    print("Получение анонимного токена...")
    token = Client.get_anonymous_token()
    print(f"Токен: {token[:20]}...")

    # Создание клиента
    client = Client(token=token)

    # Быстрый поиск
    print("\n=== Быстрый поиск 'Metallica' ===")
    results = client.quick_search("Metallica", limit=5)

    print(f"\nНайдено треков: {len(results.tracks)}")
    for track in results.tracks:
        print(f"  - {track.title} - {track.get_artists_str()} ({track.get_duration_str()})")

    print(f"\nНайдено артистов: {len(results.artists)}")
    for artist in results.artists:
        print(f"  - {artist.title}")

    print(f"\nНайдено релизов: {len(results.releases)}")
    for release in results.releases[:3]:
        print(f"  - {release.title}")

    # Получение информации о треке
    if results.tracks:
        track = results.tracks[0]
        print(f"\n=== Информация о треке '{track.title}' ===")
        full_track = client.get_track(track.id)
        if full_track:
            print(f"ID: {full_track.id}")
            print(f"Название: {full_track.title}")
            print(f"Артисты: {full_track.get_artists_str()}")
            print(f"Длительность: {full_track.get_duration_str()}")
            print(f"Explicit: {full_track.explicit}")
            print(f"FLAC доступен: {full_track.has_flac}")

            # Попробуем получить URL стрима
            try:
                stream_url = client.get_stream_url(track.id, quality=Quality.MID)
                print(f"Stream URL (mid): {stream_url[:50]}...")
            except Exception as e:
                print(f"Ошибка получения стрима: {e}")

    # Информация об артисте
    if results.artists:
        artist = results.artists[0]
        print(f"\n=== Информация об артисте '{artist.title}' ===")
        full_artist = client.get_artist(
            artist.id,
            with_popular_tracks=True,
            tracks_limit=5,
        )
        if full_artist:
            print(f"ID: {full_artist.id}")
            print(f"Название: {full_artist.title}")
            if full_artist.description:
                print(f"Описание: {full_artist.description[:100]}...")
            print(f"Популярные треки ({len(full_artist.popular_tracks)}):")
            for t in full_artist.popular_tracks[:5]:
                print(f"  - {t.title}")


if __name__ == "__main__":
    main()
