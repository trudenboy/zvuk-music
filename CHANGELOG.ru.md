# Список изменений

Все значимые изменения проекта документируются в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
проект придерживается [Semantic Versioning](https://semver.org/lang/ru/).

## [0.6.1] - 2026-03-18

### Исправлено

- Исправлен `Throttler(rate_limit=0)`, вызывавший `ZeroDivisionError`, и отрицательные значения, вызывавшие бесконечный цикл — добавлена валидация параметров
- Исправлен `Client(rate_limit=-1)`, молча создававший сломанный throttler — добавлена ранняя проверка
- Исправлен docstring async-клиента, ошибочно указывавший «Synchronous» вместо «Asynchronous» в сгенерированном `client_async.py`
- Исправлен docstring `_request_wrapper` — добавлен `RateLimitError` в секцию `Raises:`
- Исправлены нестабильные тесты throttler с жёсткими таймингами — расширены верхние границы для CI
- Исправлен `get_direct_stream_url` — теперь используется паттерн `DirectStream.de_json` вместо ручного создания

### Добавлено

- `RateLimitError.__str__` теперь показывает значение `retry_after`
- Валидация width/height в `Image.get_url()` (должны быть положительными)
- Перекрёстные ссылки в docstring между `Quality` и `StreamQuality` для предотвращения путаницы
- Предупреждение в docstring `Throttler` о недопустимости смешивания sync/async на одном экземпляре
- Тесты: валидация throttler (ноль/отрицательные), подключение rate_limit в клиенте, нецелочисленный заголовок `Retry-After`

## [0.6.0] - 2026-03-18

### Добавлено

- Исключение `RateLimitError` для HTTP 429 ответов с опциональным полем `retry_after`
- Enum `StreamQuality` для качества прямого стрима (без DRM) через Tiny API
- Enum `LyricsType` для типа формата текста песни (синхронизированный LRC / обычный текст)
- Модель `Lyrics` со свойствами `is_synced` и `lyrics_type`
- Модель `DirectStream` для прямых URL стримов (без DRM)
- Модель `GridContentItem` для элементов сетки редакторского контента
- `Client.get_direct_stream_url()` — получение прямого URL стрима через Tiny API
- `Client.get_lyrics()` — получение текста песни (LRC или обычный текст)
- `Client.get_grid_content()` — получение элементов сетки редакторского контента
- `Client.get_editorial_playlist_ids()` — удобный метод для получения ID кураторских плейлистов
- Встроенный опциональный ограничитель частоты через `Client(rate_limit=N)` на основе алгоритма корзины токенов
- Утилитный класс `Throttler` с поддержкой sync и async
- Обработка HTTP 429 в слое запросов с парсингом заголовка `Retry-After`

### Изменено

- `Image.get_url()` теперь всегда устанавливает параметр `?size=WxH` (ранее только обновлял существующий)
- Версия обновлена с 0.5.3 до 0.6.0

## [0.5.2] - 2026-01-31

### Исправлено

- Исправлена проблема неопубликованной v0.5.1 на PyPI (auto-release не содержал build+publish на момент бампа v0.5.1)

### Изменено

- Все GitHub Actions объединены в один PR от dependabot (было 3 отдельных PR)
- Расписание dependabot изменено с еженедельного на ежемесячное
- Исключены ветки `dependabot/**` из push-триггера `tests.yml` (тестируются через `pull_request`)
- Исключены ветки `dependabot/**` из `auto-pr.yml` (dependabot создаёт собственные PR)

## [0.5.1] - 2026-01-31

### Изменено

- Оптимизация CI/CD: сокращение с 15 до 5 test jobs и с 3 до 2 build jobs при релизе
- Вынесен парсинг версии в переиспользуемый composite action (`.github/actions/get-version`)
- Упрощён `auto-release.yml`: убрана дублирующая матрица тестов, сохранены build+publish (необходимы из-за ограничения событий `GITHUB_TOKEN`)
- Убрана дублирующая матрица тестов из `publish.yml`; оставлен как fallback для ручных релизов
- Добавлен concurrency control в `auto-release.yml`
- Добавлена загрузка build-артефактов в `tests.yml`
- Обновлён `codecov-action` v4 → v5
- Добавлен явный `--base main` в `auto-pr.yml`
- Добавлена секция CI/CD архитектуры в CLAUDE.md

## [0.5.0] - 2026-01-31

### Изменено

- Все docstring переведены в двуязычный формат (English + `Note (RU):` с русским текстом)
- Все inline-комментарии и маркеры секций переведены на английский
- Перегенерированы async-клиент и request-файлы
- Обновлены языковые рекомендации в CLAUDE.md

## [0.4.1] - 2026-01-31

### Исправлено

- Исправлена консистентность async-клиента (перегенерация порядка импортов `request_async.py`)
- Исправлена проблема авто-релиза не запускающего публикацию на PyPI (ограничение событий `GITHUB_TOKEN`)

## [0.4.0] - 2026-01-31

### Добавлено

- Полный CI/CD pipeline на GitHub Actions
- Автоматическое создание PR с auto-merge для feature-веток
- Автоматический релиз при изменении версии в main
- Workflow публикации с проверкой версии и полным прогоном тестов перед загрузкой на PyPI
- Конфигурация Dependabot для pip и GitHub Actions зависимостей
- Конфигурация Codecov (целевое покрытие: 65% проект, 60% патч)
- Шаблон pull request

### Изменено

- Workflow тестов: триггер на все ветки, concurrency, кэширование pip, jobs для build и async-check, порог покрытия (65%)
- Workflow публикации: проверка версии, матрица тестов и проверка async-клиента перед публикацией

## [0.3.0] - 2026-01-31

### Добавлено

- Комплексный набор тестов: base, client, exceptions, request errors, utils, models
- Тесты для всех типов моделей: artist, book, collection, common, playlist, podcast, release, search

### Изменено

- Улучшение качества кода в клиенте и моделях
- Исправление граничных случаев десериализации моделей

## [0.2.0] - 2026-01-31

### Добавлено

- CLI-скрипт `scripts/zvuk_cli.py`, оборачивающий все 58 методов Client в argparse-субкоманды
- Глобальные флаги CLI: `--token`, `--pretty`, `--timeout`, `--proxy`
- Поддержка токена через переменную окружения `ZVUK_TOKEN`
- Вывод в JSON (компактный по умолчанию, `--pretty` для отступов)

### Изменено

- Вся документация (README, CHANGELOG, CLAUDE.md) переведена на английский
- Удалены упоминания брендинга из всех файлов
- Добавлены русскоязычные версии документации (README.ru.md, CHANGELOG.ru.md)

## [0.1.3] - 2026-01-30

### Исправлено

- Исправлены имена переменных GraphQL для всех мутаций (`itemId` -> `id`, `itemType` -> `type`, `playlistId` -> `id`)
- Исправлен парсинг вложенных ключей ответа для мутаций playlist, collection и hidden_collection
- Исправлен формат входного типа `PlaylistItem` (`itemId` -> `item_id` согласно схеме API)
- Исправлен ключ ответа `get_listened_episodes` (`get_play_state.episodes`)
- Исправлен ключ ответа `get_profile_followers_count` (`collection_item_data.likes_count`)

## [0.1.2] - 2026-01-30

### Исправлено

- Исправлены 13 неверных ключей ответа API в клиентских методах:
  - `get_playlists`, `get_short_playlist`, `get_playlist_tracks`
  - `get_podcasts`, `get_episodes`
  - `get_collection`, `get_hidden_collection`
  - `get_liked_tracks`, `get_user_playlists`, `get_user_paginated_podcasts`
  - `get_hidden_tracks`, `get_following_count`, `has_unread_notifications`
  - `get_synthesis_playlists`

## [0.1.1] - 2026-01-30

### Исправлено

- Полное исправление всех ошибок mypy (390 -> 0)
- Добавлен `@dataclass_transform()` для декоратора `@model`
- Исправлены типы `TypeGuard` в `base.py`
- Исправлены return-типы в `request.py` и `response.py`
- Убраны все `# type: ignore` комментарии из `client.py`
- Добавлены mypy overrides для нетипизированных зависимостей

## [0.1.0] - 2025-01-30

### Добавлено

- Первый публичный релиз
- Синхронный клиент (`Client`) с 59 методами API
- Асинхронный клиент (`ClientAsync`) с автогенерацией из синхронной версии
- 37 моделей данных (Track, Artist, Release, Playlist, Podcast и др.)
- Поддержка GraphQL API Zvuk.com (27 запросов, 13 мутаций)
- Поиск треков, артистов, релизов, плейлистов и подкастов
- Управление плейлистами (создание, редактирование, удаление)
- Работа с коллекцией пользователя
- Получение стримов в различном качестве (MP3, FLAC, HQ FLAC)
- Работа с подкастами и эпизодами
- Поддержка анонимного доступа через токен
- PEP 561 совместимость (py.typed)
