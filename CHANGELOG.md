# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.5.1] - 2026-01-31

### Changed

- Optimize CI/CD: reduce release pipeline from 15 to 5 test jobs, 3 to 2 build jobs
- Extract version parsing into reusable composite action (`.github/actions/get-version`)
- Simplify `auto-release.yml` to only create releases (remove duplicate test/build/publish)
- Remove duplicate test matrix from `publish.yml` (trusts `tests.yml`)
- Add concurrency control to `auto-release.yml`
- Upload build artifacts in `tests.yml`
- Bump `codecov-action` v4 to v5
- Add explicit `--base main` to `auto-pr.yml`
- Add CI/CD architecture section to CLAUDE.md

## [0.5.0] - 2026-01-31

### Changed

- Translate all docstrings to bilingual format (English + `Note (RU):` with Russian)
- Translate all inline comments and section markers to English
- Regenerate async client and request files
- Update CLAUDE.md language guidelines

## [0.4.1] - 2026-01-31

### Fixed

- Fix async client consistency (regenerate `request_async.py` import order)
- Fix auto-release not triggering PyPI publish (`GITHUB_TOKEN` event limitation)

## [0.4.0] - 2026-01-31

### Added

- Full CI/CD pipeline with GitHub Actions
- Auto-PR creation with auto-merge for feature branches
- Auto-release on version bump in main
- Publish workflow with version verification and full test matrix before PyPI upload
- Dependabot configuration for pip and GitHub Actions dependencies
- Codecov configuration (65% project target, 60% patch target)
- Pull request template

### Changed

- Tests workflow: trigger on all branches, add concurrency, pip caching, build and async-check jobs, coverage threshold (65%)
- Publish workflow: add version-check, test matrix, and async-consistency verification before publishing

## [0.3.0] - 2026-01-31

### Added

- Comprehensive test suite: base, client, exceptions, request errors, utils, models
- Tests for all model types: artist, book, collection, common, playlist, podcast, release, search

### Changed

- Improve code quality across client and models
- Fix model deserialization edge cases

## [0.2.0] - 2026-01-31

### Added

- CLI script `scripts/zvuk_cli.py` wrapping all 58 Client methods as argparse subcommands
- CLI supports global flags: `--token`, `--pretty`, `--timeout`, `--proxy`
- Token can be provided via `ZVUK_TOKEN` environment variable
- JSON output (compact by default, `--pretty` for indented)

### Changed

- Translate all documentation (README, CHANGELOG, CLAUDE.md) to English
- Remove branding references from all files

## [0.1.3] - 2026-01-30

### Fixed

- Fix GraphQL variable names for all mutations (`itemId` -> `id`, `itemType` -> `type`, `playlistId` -> `id`)
- Fix nested response key parsing for playlist, collection, and hidden_collection mutations
- Fix `PlaylistItem` input type format (`itemId` -> `item_id` per API schema)
- Fix `get_listened_episodes` response key (`get_play_state.episodes`)
- Fix `get_profile_followers_count` response key (`collection_item_data.likes_count`)

## [0.1.2] - 2026-01-30

### Fixed

- Fix 13 incorrect API response keys in client methods:
  - `get_playlists`, `get_short_playlist`, `get_playlist_tracks`
  - `get_podcasts`, `get_episodes`
  - `get_collection`, `get_hidden_collection`
  - `get_liked_tracks`, `get_user_playlists`, `get_user_paginated_podcasts`
  - `get_hidden_tracks`, `get_following_count`, `has_unread_notifications`
  - `get_synthesis_playlists`

## [0.1.1] - 2026-01-30

### Fixed

- Fix all mypy type errors (390 -> 0)
- Add `@dataclass_transform()` to `@model` decorator
- Fix `TypeGuard` types in `base.py`
- Fix return types in `request.py` and `response.py`
- Remove all `# type: ignore` comments from `client.py`
- Add mypy overrides for untyped dependencies

## [0.1.0] - 2025-01-30

### Added

- Initial public release
- Synchronous client (`Client`) with 59 API methods
- Async client (`ClientAsync`) auto-generated from the synchronous version
- 37 data models (Track, Artist, Release, Playlist, Podcast, etc.)
- GraphQL API support for Zvuk.com (27 queries, 13 mutations)
- Search for tracks, artists, releases, playlists, and podcasts
- Playlist management (create, edit, delete)
- User collection management
- Audio streaming in multiple qualities (MP3, FLAC, HQ FLAC)
- Podcast and episode support
- Anonymous access via token
- PEP 561 compatibility (py.typed)
