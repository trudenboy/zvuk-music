"""Quick start example with Zvuk Music API."""

from zvuk_music import Client, Quality


def main() -> None:
    # Get anonymous token
    print("Getting anonymous token...")
    token = Client.get_anonymous_token()
    print(f"Token: {token[:20]}...")

    # Create client
    client = Client(token=token)

    # Quick search
    print("\n=== Quick search 'Metallica' ===")
    results = client.quick_search("Metallica", limit=5)

    print(f"\nTracks found: {len(results.tracks)}")
    for track in results.tracks:
        print(f"  - {track.title} - {track.get_artists_str()} ({track.get_duration_str()})")

    print(f"\nArtists found: {len(results.artists)}")
    for artist in results.artists:
        print(f"  - {artist.title}")

    print(f"\nReleases found: {len(results.releases)}")
    for release in results.releases[:3]:
        print(f"  - {release.title}")

    # Get track information
    if results.tracks:
        track = results.tracks[0]
        print(f"\n=== Track info '{track.title}' ===")
        full_track = client.get_track(track.id)
        if full_track:
            print(f"ID: {full_track.id}")
            print(f"Title: {full_track.title}")
            print(f"Artists: {full_track.get_artists_str()}")
            print(f"Duration: {full_track.get_duration_str()}")
            print(f"Explicit: {full_track.explicit}")
            print(f"FLAC available: {full_track.has_flac}")

            # Try to get stream URL
            try:
                stream_url = client.get_stream_url(track.id, quality=Quality.MID)
                print(f"Stream URL (mid): {stream_url[:50]}...")
            except Exception as e:
                print(f"Error getting stream: {e}")

    # Artist information
    if results.artists:
        artist = results.artists[0]
        print(f"\n=== Artist info '{artist.title}' ===")
        full_artist = client.get_artist(
            artist.id,
            with_popular_tracks=True,
            tracks_limit=5,
        )
        if full_artist:
            print(f"ID: {full_artist.id}")
            print(f"Title: {full_artist.title}")
            if full_artist.description:
                print(f"Description: {full_artist.description[:100]}...")
            print(f"Popular tracks ({len(full_artist.popular_tracks)}):")
            for t in full_artist.popular_tracks[:5]:
                print(f"  - {t.title}")


if __name__ == "__main__":
    main()
