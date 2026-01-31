"""Example of using the asynchronous client."""

import asyncio

from zvuk_music import Client, ClientAsync


async def main() -> None:
    # Get anonymous token (synchronous method)
    print("=== Getting token ===")
    token = Client.get_anonymous_token()
    print(f"Token: {token[:20]}...")

    # Create async client
    client = ClientAsync(token=token)

    # Quick search
    print("\n=== Async quick search 'Metallica' ===")
    results = await client.quick_search("Metallica", limit=5)

    print(f"Tracks found: {len(results.tracks)}")
    for track in results.tracks:
        print(f"  - {track.title} - {track.get_artists_str()}")

    print(f"Artists found: {len(results.artists)}")
    for artist in results.artists:
        print(f"  - {artist.title}")

    # Fetch multiple items in parallel
    print("\n=== Parallel data fetching ===")

    # Launch several requests in parallel
    track_task = client.get_track(5896627)
    artist_task = client.get_artist(754367, with_popular_tracks=True, tracks_limit=3)
    search_task = client.search("Nothing Else Matters", limit=3)

    track, artist, search = await asyncio.gather(track_task, artist_task, search_task)

    print(f"\nTrack: {track.title if track else 'N/A'}")
    print(f"Artist: {artist.title if artist else 'N/A'}")
    if artist:
        print(f"  Popular tracks: {len(artist.popular_tracks)}")
    if search and search.tracks:
        print(f"Found in search: {len(search.tracks.items)} tracks")

    # Get stream
    print("\n=== Getting stream URLs ===")
    streams = await client.get_stream_urls([5896627, 5896623])
    print(f"Got {len(streams)} streams")
    for stream in streams:
        print(f"  Mid URL available: {'yes' if stream.mid else 'no'}")

    print("\n=== Async tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())
