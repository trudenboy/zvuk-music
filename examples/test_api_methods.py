"""Тестирование различных методов API."""

from zvuk_music import Client, Quality


def main() -> None:
    # Получение анонимного токена
    print("=== Получение токена ===")
    token = Client.get_anonymous_token()
    print(f"Токен: {token[:20]}...")

    # Создание клиента
    client = Client(token=token)

    # Тест профиля
    print("\n=== Профиль ===")
    profile = client.get_profile()
    print(f"ID: {profile.result.id}")
    print(f"Анонимный: {profile.result.is_anonymous}")
    print(f"Авторизован: {profile.result.is_authorized()}")

    # Тест полного поиска
    print("\n=== Полный поиск 'Metallica' ===")
    search = client.search("Metallica", limit=3)
    if search:
        print(f"Search ID: {search.search_id}")
        if search.tracks:
            print(f"Треков найдено: {search.tracks.page.total if search.tracks.page else 'N/A'}")
            for track in search.tracks.items[:3]:
                print(f"  - {track.title} - {track.get_artists_str()}")
        if search.artists:
            print(f"Артистов найдено: {search.artists.page.total if search.artists.page else 'N/A'}")
            for artist in search.artists.items[:3]:
                print(f"  - {artist.title}")
        if search.releases:
            print(f"Релизов найдено: {search.releases.page.total if search.releases.page else 'N/A'}")
            for release in search.releases.items[:3]:
                print(f"  - {release.title}")

    # Тест получения трека
    print("\n=== Получение трека 5896627 ===")
    track = client.get_track(5896627)
    if track:
        print(f"ID: {track.id}")
        print(f"Название: {track.title}")
        print(f"Артисты: {track.get_artists_str()}")
        print(f"Длительность: {track.get_duration_str()}")
        print(f"Explicit: {track.explicit}")
        print(f"Availability: {track.availability}")

    # Тест получения нескольких треков
    print("\n=== Получение нескольких треков ===")
    tracks = client.get_tracks([5896627, 5896623, 5896628])
    print(f"Получено треков: {len(tracks)}")
    for t in tracks:
        print(f"  - {t.title}")

    # Тест получения релиза
    print("\n=== Получение релиза ===")
    release = client.get_release(669414)  # Metallica - Black Album
    if release:
        print(f"ID: {release.id}")
        print(f"Название: {release.title}")
        print(f"Тип: {release.type}")
        print(f"Дата: {release.date}")
        print(f"Артисты: {', '.join(a.title for a in release.artists)}")
        print(f"Треков: {len(release.tracks)}")
        if release.tracks:
            for i, t in enumerate(release.tracks[:5], 1):
                print(f"  {i}. {t.title}")

    # Тест получения артиста с релизами
    print("\n=== Получение артиста с релизами ===")
    artist = client.get_artist(
        754367,
        with_releases=True,
        releases_limit=5,
        with_popular_tracks=True,
        tracks_limit=5,
        with_description=True,
    )
    if artist:
        print(f"ID: {artist.id}")
        print(f"Название: {artist.title}")
        if artist.description:
            print(f"Описание: {artist.description[:100]}...")
        print(f"Релизов: {len(artist.releases)}")
        for r in artist.releases[:3]:
            print(f"  - {r.title} ({r.type})")
        print(f"Популярных треков: {len(artist.popular_tracks)}")

    # Тест получения URL стрима
    print("\n=== Получение URL стрима ===")
    try:
        stream_url = client.get_stream_url(5896627, quality=Quality.MID)
        print(f"Mid quality URL: {stream_url[:60]}...")
    except Exception as e:
        print(f"Ошибка: {e}")

    # Тест получения объекта Stream
    print("\n=== Получение объектов Stream ===")
    streams = client.get_stream_urls([5896627, 5896623])
    print(f"Получено стримов: {len(streams)}")
    for stream in streams:
        print(f"  - Mid: {stream.mid[:50] if stream.mid else 'N/A'}...")
        print(f"    High: {'доступен' if stream.high else 'недоступен'}")
        print(f"    FLAC: {'доступен' if stream.flacdrm else 'недоступен'}")
        print(f"    Истекает через: {stream.expire_delta} сек")

    print("\n=== Все тесты завершены ===")


if __name__ == "__main__":
    main()
