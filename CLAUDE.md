# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**zvuk-music** is a Python library for the Zvuk.com music streaming API. It provides both synchronous and asynchronous interfaces for accessing music content, managing playlists, retrieving tracks, and handling user collections.

- **Version**: 0.5.2
- **License**: MIT
- **Language**: Python 3.9+

## Build Commands

```bash
# Install dependencies
pip install -e ".[dev]"          # Development install with all deps
pip install -e ".[async]"        # With async support (aiohttp)
pip install -e ".[fast]"         # With fast JSON (ujson)

# Run tests
pytest                           # Run all tests
pytest tests/test_models/        # Run model tests only
pytest --cov=zvuk_music          # With coverage

# Linting and formatting
ruff check zvuk_music            # Check for lint errors
ruff format zvuk_music           # Format code
mypy zvuk_music                  # Type checking

# Generate async client from sync version
python scripts/generate_async_version.py
```

## Architecture

### Directory Structure

- `zvuk_music/` - Main library package
  - `client.py` - Synchronous API client (58 methods)
  - `client_async.py` - Auto-generated async client
  - `models/` - Data models (Track, Artist, Release, Playlist, etc.)
  - `graphql/queries/` - GraphQL query files (25 files)
  - `graphql/mutations/` - GraphQL mutation files (11 files)
  - `utils/` - HTTP request handlers and utilities
  - `base.py` - Base classes (ZvukMusicModel, ZvukMusicObject)
  - `enums.py` - Enumerations (Quality, ReleaseType, OrderBy)
  - `exceptions.py` - Custom exception classes
- `tests/` - Test suite
- `examples/` - Usage examples
- `scripts/` - Utility scripts

### Key Patterns

1. **Async Generation**: `client_async.py` and `request_async.py` are auto-generated from their sync counterparts via `scripts/generate_async_version.py`. Edit the sync versions only.

2. **Models**: All models use `@model` decorator (dataclass wrapper), inherit from `ZvukMusicModel`, and implement `de_json()` / `de_list()` for deserialization.

3. **GraphQL**: API uses GraphQL endpoint at `https://zvuk.com/api/v1/graphql`. Query files are in `zvuk_music/graphql/`.

## Code Style

- **Line length**: 100 characters
- **Formatting**: Ruff (double quotes, 4-space indent)
- **Type hints**: Full mypy compliance required
- **Language**: English for code comments; bilingual (EN + RU) for docstrings
- **Import sorting**: isort via Ruff

## CI/CD

GitHub Actions workflows in `.github/workflows/`:

- **`tests.yml`** — Runs on every push/PR. Jobs: lint (ruff + mypy), build (package + upload artifact), async-check (regenerate & diff), test matrix (Python 3.9–3.13, 65% coverage threshold). Codecov upload on 3.12.
- **`auto-release.yml`** — Runs on push to main. Compares `__version__` with latest git tag; if changed: creates GitHub release, builds package (with async-check), publishes to PyPI. Build and publish are embedded because `GITHUB_TOKEN`-created releases don't trigger other workflows.
- **`publish.yml`** — Fallback for manually-created releases. Triggered by `release: published` event. Jobs: version-check (tag matches `__version__`), build (with async-check), publish to PyPI via OIDC.
- **`auto-pr.yml`** — Runs on push to non-main branches. Creates PR with `--base main` and enables auto-merge (squash).
- **`dependabot.yml`** — Monthly updates for pip (dev deps grouped) and GitHub Actions (grouped into single PR).

Shared logic:

- **`.github/actions/get-version/action.yml`** — Composite action that extracts version from `zvuk_music/__init__.py`. Used by `auto-release.yml` and `publish.yml`.

Release flow: push to main → `tests.yml` validates → `auto-release.yml` creates release → `publish.yml` builds & publishes to PyPI.

## Testing

Tests use pytest with fixtures in `tests/conftest.py`. Model tests are in `tests/test_models/`. Use `pytest-asyncio` for async tests.
