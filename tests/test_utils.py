"""Тесты утилит."""

import pytest

from zvuk_music.utils.graphql import load_query
from zvuk_music.utils.request import Request


class TestLoadQuery:
    """Тесты загрузки GraphQL запросов."""

    def test_load_query_exists(self):
        """Загрузка существующего запроса."""
        query = load_query("getTracks")
        assert "query" in query.lower() or "mutation" in query.lower() or "getTracks" in query

    def test_load_query_mutation(self):
        """Загрузка существующей мутации."""
        query = load_query("createPlaylist")
        assert len(query) > 0

    def test_load_query_not_found(self):
        """Несуществующий файл вызывает FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_query("nonExistentQuery_12345")


class TestCamelToSnake:
    """Тесты конвертации CamelCase в snake_case."""

    def test_simple(self):
        assert Request._convert_camel_to_snake("camelCase") == "camel_case"

    def test_with_consecutive_uppers(self):
        assert Request._convert_camel_to_snake("getHTTPResponse") == "get_http_response"

    def test_already_snake(self):
        assert Request._convert_camel_to_snake("already_snake") == "already_snake"

    def test_single_word(self):
        assert Request._convert_camel_to_snake("word") == "word"

    def test_pascal_case(self):
        assert Request._convert_camel_to_snake("PascalCase") == "pascal_case"

    def test_mixed(self):
        assert Request._convert_camel_to_snake("searchSessionId") == "search_session_id"


class TestObjectHook:
    """Тесты нормализации ключей API ответа."""

    def test_camel_to_snake(self):
        """CamelCase ключи конвертируются."""
        result = Request._object_hook({"searchTitle": "test", "hasFlac": True})
        assert "search_title" in result
        assert "has_flac" in result

    def test_non_dict_passthrough(self):
        """Не-словарь возвращается без изменений."""
        assert Request._object_hook([1, 2, 3]) == [1, 2, 3]
        assert Request._object_hook("string") == "string"

    def test_reserved_word_escape(self):
        """Зарезервированные слова Python получают суффикс _."""
        # 'class' is a Python keyword, 'type' is not (it's a builtin)
        result = Request._object_hook({"class": "Rock"})
        assert "class_" in result

    def test_client_reserved(self):
        """'client' также экранируется."""
        result = Request._object_hook({"client": "value"})
        assert "client_" in result

    def test_hyphen_replacement(self):
        """Дефисы заменяются на подчёркивания."""
        result = Request._object_hook({"content-type": "json"})
        assert "content_type" in result

    def test_digit_prefix(self):
        """Ключи начинающиеся с цифры получают префикс _."""
        result = Request._object_hook({"1key": "value"})
        assert "_1key" in result
