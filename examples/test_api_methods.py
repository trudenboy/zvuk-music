"""Testing various API methods."""

from zvuk_music import Client, Quality


def main() -> None:
    # Get anonymous token
    print("=== Getting token ===")
    token = Client.get_anonymous_token()
    print(f"Token: {token[:20]}...")

    # Create client
    client = Client(token=token)

    # Test profile
    print("\n=== Profile ===")
    profile = client.get_profile()
    print(f"ID: {profile.result.id}")
    print(f"Anonymous: {profile.result.is_anonymous}")
    print(f"Authorized: {profile.result.is_authorized()}")

    # Test full search
    print("\n=== Full search 'Metallica' ===")
    search = client.search("Metallica", limit=3)
    if search:
        print(f"Search ID: {search.search_id}")
        if search.tracks:
            print(f"Tracks found: {search.tracks.page.total if search.tracks.page else 'N/A'}")
            for track in search.tracks.items[:3]:
                print(f"  - {track.title} - {track.get_artists_str()}")
        if search.artists:
            print(f"Artists found: {search.artists.page.total if search.artists.page else 'N/A'}")
            for artist in search.artists.items[:3]:
                print(f"  - {artist.title}")
        if search.releases:
            print(f"Releases found: {search.releases.page.total if search.releases.page else 'N/A'}")
            for release in search.releases.items[:3]:
                print(f"  - {release.title}")

    # Test getting a track
    print("\n=== Getting track 5896627 ===")
    track = client.get_track(5896627)
    if track:
        print(f"ID: {track.id}")
        print(f"Title: {track.title}")
        print(f"Artists: {track.get_artists_str()}")
        print(f"Duration: {track.get_duration_str()}")
        print(f"Explicit: {track.explicit}")
        print(f"Availability: {track.availability}")

    # Test getting multiple tracks
    print("\n=== Getting multiple tracks ===")
    tracks = client.get_tracks([5896627, 5896623, 5896628])
    print(f"Tracks received: {len(tracks)}")
    for t in tracks:
        print(f"  - {t.title}")

    # Test getting a release
    print("\n=== Getting release ===")
    release = client.get_release(669414)  # Metallica - Black Album
    if release:
        print(f"ID: {release.id}")
        print(f"Title: {release.title}")
        print(f"Type: {release.type}")
        print(f"Date: {release.date}")
        print(f"Artists: {', '.join(a.title for a in release.artists)}")
        print(f"Tracks: {len(release.tracks)}")
        if release.tracks:
            for i, t in enumerate(release.tracks[:5], 1):
                print(f"  {i}. {t.title}")

    # Test getting artist with releases
    print("\n=== Getting artist with releases ===")
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
        print(f"Title: {artist.title}")
        if artist.description:
            print(f"Description: {artist.description[:100]}...")
        print(f"Releases: {len(artist.releases)}")
        for r in artist.releases[:3]:
            print(f"  - {r.title} ({r.type})")
        print(f"Popular tracks: {len(artist.popular_tracks)}")

    # Test getting stream URL
    print("\n=== Getting stream URL ===")
    try:
        stream_url = client.get_stream_url(5896627, quality=Quality.MID)
        print(f"Mid quality URL: {stream_url[:60]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Test getting Stream objects
    print("\n=== Getting Stream objects ===")
    streams = client.get_stream_urls([5896627, 5896623])
    print(f"Streams received: {len(streams)}")
    for stream in streams:
        print(f"  - Mid: {stream.mid[:50] if stream.mid else 'N/A'}...")
        print(f"    High: {'available' if stream.high else 'unavailable'}")
        print(f"    FLAC: {'available' if stream.flacdrm else 'unavailable'}")
        print(f"    Expires in: {stream.expire_delta} sec")

    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()
