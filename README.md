# Zvuk Music API

Unofficial Python library for the [Zvuk.com](https://zvuk.com) music streaming API.

**[Документация на русском / Russian documentation](README.ru.md)**

> **Disclaimer:** This library is not affiliated with or endorsed by Zvuk.com. It was built by analyzing the Zvuk.com web application and studying existing open-source projects (see [References](#references)).

## Installation

```bash
pip install zvuk-music
```

With async support:

```bash
pip install zvuk-music[async]
```

With faster JSON parsing:

```bash
pip install zvuk-music[fast]
```

## Quick Start

### Anonymous Access

```python
from zvuk_music import Client

# Get an anonymous token (limited functionality)
token = Client.get_anonymous_token()
client = Client(token=token)

# Search
results = client.quick_search("Metallica")
for track in results.tracks[:5]:
    print(f"{track.title} - {track.get_artists_str()}")
```

### Authorized Access

For full functionality (high quality, likes, playlists) you need an authorized user token:

1. Log in to [zvuk.com](https://zvuk.com) in your browser
2. Open https://zvuk.com/api/tiny/profile
3. Copy the `token` field value

```python
from zvuk_music import Client

client = Client(token="your_token")

# Get artist info
artist = client.get_artist(754367, with_popular_tracks=True)
print(f"{artist.title}")
for track in artist.popular_tracks[:5]:
    print(f"  - {track.title}")
```

## Usage Examples

### Search

```python
# Quick search (autocomplete)
quick = client.quick_search("Nothing Else Matters", limit=5)

# Full-text search
search = client.search("Metallica", limit=10)
print(f"Tracks found: {search.tracks.page.total}")
print(f"Artists found: {search.artists.page.total}")
```

### Tracks

```python
# Get a track
track = client.get_track(5896627)
print(f"{track.title} ({track.get_duration_str()})")

# Get stream URL
from zvuk_music import Quality

url = client.get_stream_url(track.id, quality=Quality.HIGH)
print(f"Stream URL: {url}")

# Download track
track.download("metallica_nothing_else_matters.mp3", quality=Quality.MID)
```

### Playlists

```python
# Create a playlist
playlist_id = client.create_playlist("My Playlist", track_ids=["5896627", "5896628"])

# Add tracks
client.add_tracks_to_playlist(playlist_id, ["5896629", "5896630"])

# Get playlist
playlist = client.get_playlist(playlist_id)
for track in playlist.tracks:
    print(f"  - {track.title}")

# Delete playlist
client.delete_playlist(playlist_id)
```

### Collection (Likes)

```python
# Like a track
client.like_track(5896627)

# Get liked tracks
from zvuk_music import OrderBy, OrderDirection

liked = client.get_liked_tracks(
    order_by=OrderBy.DATE_ADDED,
    direction=OrderDirection.DESC
)
for track in liked[:10]:
    print(f"{track.title} - {track.get_artists_str()}")

# Remove like
client.unlike_track(5896627)
```

### Artists and Releases

```python
# Artist info
artist = client.get_artist(
    754367,  # Metallica
    with_releases=True,
    with_popular_tracks=True,
    with_related_artists=True,
)

print(f"Artist: {artist.title}")
print(f"Releases: {len(artist.releases)}")
print(f"Popular tracks: {len(artist.popular_tracks)}")

# Get a release
release = client.get_release(artist.releases[0].id)
print(f"\nAlbum: {release.title} ({release.get_year()})")
for track in release.tracks:
    print(f"  {track.position}. {track.title}")
```

## Audio Quality

| Quality | Bitrate | Subscription required |
|---------|---------|----------------------|
| `Quality.MID` | 128kbps MP3 | No |
| `Quality.HIGH` | 320kbps MP3 | Yes |
| `Quality.FLAC` | FLAC | Yes |

```python
from zvuk_music import Quality, SubscriptionRequiredError

try:
    url = client.get_stream_url(track_id, quality=Quality.HIGH)
except SubscriptionRequiredError:
    # Fallback to mid quality
    url = client.get_stream_url(track_id, quality=Quality.MID)
```

## Error Handling

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
    print("Track not found")
except UnauthorizedError:
    print("Invalid token")
except BotDetectedError:
    print("API blocked the request (bot protection)")
except ZvukMusicError as e:
    print(f"Error: {e}")
```

## Async Client

```python
import asyncio
from zvuk_music import Client, ClientAsync

async def main():
    token = Client.get_anonymous_token()
    client = ClientAsync(token=token)

    # Parallel requests
    track, artist = await asyncio.gather(
        client.get_track(5896627),
        client.get_artist(754367, with_popular_tracks=True),
    )
    print(f"{track.title} — {artist.title}")

asyncio.run(main())
```

Installation: `pip install zvuk-music[async]`

## CLI

The `scripts/zvuk_cli.py` script provides access to all 58 API methods via the command line. Output is JSON.

### Usage

```bash
python scripts/zvuk_cli.py <subcommand> [arguments]
```

### Global Flags

| Flag | Description |
|------|-------------|
| `-t`, `--token` | Auth token (also read from `ZVUK_TOKEN` env var) |
| `-p`, `--pretty` | Pretty-print JSON (indent=2) |
| `--timeout` | Request timeout in seconds (default: 10) |
| `--proxy` | Proxy server URL |

### Examples

```bash
# Get an anonymous token
python scripts/zvuk_cli.py get-anonymous-token

# Search (with pretty output)
python scripts/zvuk_cli.py -p quick-search "Metallica" --limit 3

# Get a track
python scripts/zvuk_cli.py -p track-get 5896627

# Artist info with releases
python scripts/zvuk_cli.py -p artist-get 754367 --with-releases --releases-limit 5

# Using a token via environment variable
export ZVUK_TOKEN=<your_token>
python scripts/zvuk_cli.py -p collection-liked-tracks --order-by dateAdded
python scripts/zvuk_cli.py -p like-track 5896627

# Create a playlist
python scripts/zvuk_cli.py -p playlist-create "My Playlist" --track-ids 5896627 5896628

# Full-text search without podcasts and books
python scripts/zvuk_cli.py -p search "Nothing Else Matters" --no-podcasts --no-books
```

### All Subcommands

**Auth:**
`get-anonymous-token`, `init`, `get-profile`, `is-authorized`

**Search:**
`quick-search`, `search`

**Tracks:**
`track-get`, `tracks-get`, `track-get-full`, `stream-url`, `stream-urls`

**Releases:**
`release-get`, `releases-get`

**Artists:**
`artist-get`, `artists-get`

**Playlists:**
`playlist-get`, `playlists-get`, `playlist-get-short`, `playlist-tracks`,
`playlist-create`, `playlist-delete`, `playlist-rename`, `playlist-add-tracks`,
`playlist-update`, `playlist-set-public`, `synthesis-playlist-build`, `synthesis-playlists-get`

**Podcasts:**
`podcast-get`, `podcasts-get`, `episode-get`, `episodes-get`

**Collection:**
`collection-get`, `collection-liked-tracks`, `collection-playlists`, `collection-podcasts`,
`collection-add`, `collection-remove`,
`like-track`, `unlike-track`, `like-release`, `unlike-release`,
`like-artist`, `unlike-artist`, `like-playlist`, `unlike-playlist`,
`like-podcast`, `unlike-podcast`

**Hidden:**
`hidden-collection`, `hidden-tracks`, `hidden-add`, `hidden-remove`,
`hide-track`, `unhide-track`

**Profiles:**
`profile-followers-count`, `profile-following-count`

**History:**
`listening-history`, `listened-episodes`, `has-unread-notifications`

Help for any subcommand: `python scripts/zvuk_cli.py <subcommand> --help`

## API Reference

### Client

58 methods. All methods are available in both the synchronous (`Client`) and asynchronous (`ClientAsync`) clients.

**Auth & Profile:**

| Method | Description |
|--------|-------------|
| `get_anonymous_token()` | Get anonymous token |
| `init()` | Initialize client (load profile) |
| `get_profile()` | User profile |
| `is_authorized()` | Check authorization |

**Search:**

| Method | Description |
|--------|-------------|
| `quick_search(query)` | Quick search (autocomplete) |
| `search(query)` | Full-text search |

**Tracks & Streaming:**

| Method | Description |
|--------|-------------|
| `get_track(id)` | Get a track |
| `get_tracks(ids)` | Get multiple tracks |
| `get_full_track(id)` | Track with artists and releases |
| `get_stream_url(id, quality)` | Stream URL |
| `get_stream_urls(ids)` | Multiple stream URLs |

**Artists & Releases:**

| Method | Description |
|--------|-------------|
| `get_artist(id)` | Artist (with releases, tracks, related) |
| `get_artists(ids)` | Multiple artists |
| `get_release(id)` | Release (album/single) |
| `get_releases(ids)` | Multiple releases |

**Playlists:**

| Method | Description |
|--------|-------------|
| `get_playlist(id)` | Get playlist |
| `get_playlists(ids)` | Multiple playlists |
| `get_playlist_tracks(id)` | Playlist tracks |
| `create_playlist(name)` | Create playlist |
| `rename_playlist(id, name)` | Rename |
| `add_tracks_to_playlist(id, track_ids)` | Add tracks |
| `update_playlist(id, track_ids)` | Update playlist |
| `set_playlist_public(id, is_public)` | Change visibility |
| `delete_playlist(id)` | Delete playlist |

**Podcasts:**

| Method | Description |
|--------|-------------|
| `get_podcast(id)` | Get podcast |
| `get_podcasts(ids)` | Multiple podcasts |
| `get_episode(id)` | Get episode |
| `get_episodes(ids)` | Multiple episodes |

**Collection (Likes):**

| Method | Description |
|--------|-------------|
| `get_collection()` | User collection |
| `get_liked_tracks()` | Liked tracks |
| `get_user_playlists()` | User playlists |
| `like_track(id)` / `unlike_track(id)` | Like / unlike track |
| `like_release(id)` / `unlike_release(id)` | Like / unlike release |
| `like_artist(id)` / `unlike_artist(id)` | Like / unlike artist |
| `like_playlist(id)` / `unlike_playlist(id)` | Like / unlike playlist |
| `like_podcast(id)` / `unlike_podcast(id)` | Like / unlike podcast |

**Hidden Collection:**

| Method | Description |
|--------|-------------|
| `get_hidden_collection()` | Hidden items |
| `get_hidden_tracks()` | Hidden tracks |
| `hide_track(id)` / `unhide_track(id)` | Hide / unhide track |

**Profiles & Social:**

| Method | Description |
|--------|-------------|
| `get_profile_followers_count(ids)` | Follower count |
| `get_following_count(id)` | Following count |
| `has_unread_notifications()` | Unread notifications |

## References

This library was designed based on analysis of the [Zvuk.com](https://zvuk.com) web application and the following open-source projects:

- [yandex-music-api](https://github.com/MarshalX/yandex-music-api) -- Python library for Yandex Music API (architecture and code style reference)
- [gozvuk](https://github.com/oklookat/gozvuk) -- Unofficial Go client for Zvuk.com API
- [sberzvuk-api](https://github.com/Aiving/sberzvuk-api) -- JavaScript/TypeScript library for Zvuk API

## License

MIT License
