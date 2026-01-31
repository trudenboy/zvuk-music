"""Тесты базовых классов."""

import json

import pytest

from zvuk_music.base import ZvukMusicModel
from zvuk_music.models.common import Genre
from zvuk_music.utils import model


@model
class _SampleModel(ZvukMusicModel):
    """Тестовая модель."""

    id: str = ""
    name: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)


class TestCleanupData:
    """Тесты cleanup_data."""

    def test_extra_fields_filtered(self, mock_client):
        """Неизвестные поля фильтруются."""
        data = {"id": "1", "name": "test", "unknown_field": "value", "another": 42}
        cleaned = _SampleModel.cleanup_data(data, mock_client)
        assert "id" in cleaned
        assert "name" in cleaned
        assert "unknown_field" not in cleaned
        assert "another" not in cleaned

    def test_report_unknown_fields(self, mock_client):
        """report_unknown_fields вызывает callback при неизвестных полях."""
        mock_client.report_unknown_fields = True
        data = {"id": "1", "name": "test", "extra": "val"}

        # Не должно вызывать ошибку
        cleaned = _SampleModel.cleanup_data(data, mock_client)
        assert "extra" not in cleaned
        mock_client.report_unknown_fields = False

    def test_none_data_returns_empty(self, mock_client):
        """None возвращает пустой словарь."""
        assert _SampleModel.cleanup_data(None, mock_client) == {}

    def test_empty_dict_returns_empty(self, mock_client):
        """Пустой словарь возвращает пустой словарь."""
        assert _SampleModel.cleanup_data({}, mock_client) == {}


class TestToDict:
    """Тесты to_dict."""

    def test_excludes_client(self, mock_client):
        """client не попадает в to_dict()."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        d = obj.to_dict()
        assert "client" not in d
        assert d["id"] == "1"
        assert d["name"] == "test"

    def test_excludes_id_attrs(self, mock_client):
        """_id_attrs не попадает в to_dict()."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        d = obj.to_dict()
        assert "_id_attrs" not in d

    def test_for_request_camel_case(self, mock_client):
        """to_dict(for_request=True) конвертирует ключи в camelCase."""
        genre = Genre(client=mock_client, id="1", name="Rock", short_name="rock")
        d = genre.to_dict(for_request=True)
        assert "shortName" in d
        assert "short_name" not in d

    def test_nested_models(self, mock_client):
        """to_dict рекурсивно сериализует вложенные модели."""
        data = {
            "id": "1",
            "name": "Rock",
            "short_name": "",
        }
        genre = Genre.de_json(data, mock_client)
        d = genre.to_dict()
        assert isinstance(d, dict)
        assert d["id"] == "1"


class TestToJson:
    """Тесты to_json."""

    def test_returns_valid_json(self, mock_client):
        """to_json() возвращает валидный JSON."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        json_str = obj.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == "1"
        assert parsed["name"] == "test"
        assert "client" not in parsed


class TestEquality:
    """Тесты __eq__."""

    def test_equality_by_id_attrs(self, mock_client):
        """__eq__ сравнивает по _id_attrs."""
        obj1 = _SampleModel(client=mock_client, id="1", name="name1")
        obj2 = _SampleModel(client=mock_client, id="1", name="name2")
        assert obj1 == obj2

    def test_inequality_by_id_attrs(self, mock_client):
        """Разные _id_attrs — неравные объекты."""
        obj1 = _SampleModel(client=mock_client, id="1", name="test")
        obj2 = _SampleModel(client=mock_client, id="2", name="test")
        assert obj1 != obj2

    def test_inequality_different_type(self, mock_client):
        """Разные типы — неравны."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        assert obj != "not a model"


class TestHash:
    """Тесты __hash__."""

    def test_hash_by_id_attrs(self, mock_client):
        """__hash__ стабилен для одинаковых id."""
        obj1 = _SampleModel(client=mock_client, id="1", name="name1")
        obj2 = _SampleModel(client=mock_client, id="1", name="name2")
        assert hash(obj1) == hash(obj2)

    def test_hash_different_id(self, mock_client):
        """Разные id — разный хеш (обычно)."""
        obj1 = _SampleModel(client=mock_client, id="1", name="test")
        obj2 = _SampleModel(client=mock_client, id="2", name="test")
        # Разные id обычно дают разный хеш
        assert hash(obj1) != hash(obj2)

    def test_usable_in_set(self, mock_client):
        """Объекты можно использовать в set."""
        obj1 = _SampleModel(client=mock_client, id="1", name="a")
        obj2 = _SampleModel(client=mock_client, id="1", name="b")
        obj3 = _SampleModel(client=mock_client, id="2", name="c")
        s = {obj1, obj2, obj3}
        assert len(s) == 2


class TestDeJson:
    """Тесты базового de_json."""

    def test_de_json_valid(self, mock_client):
        """Базовый de_json работает."""
        obj = _SampleModel.de_json({"id": "1", "name": "test"}, mock_client)
        assert obj is not None
        assert obj.id == "1"

    def test_de_json_none(self, mock_client):
        """de_json(None) возвращает None."""
        assert _SampleModel.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        """de_json({}) возвращает None."""
        assert _SampleModel.de_json({}, mock_client) is None

    def test_de_list_valid(self, mock_client):
        """de_list работает со списком."""
        data = [{"id": "1", "name": "a"}, {"id": "2", "name": "b"}]
        items = _SampleModel.de_list(data, mock_client)
        assert len(items) == 2

    def test_de_list_empty(self, mock_client):
        """de_list([]) возвращает пустой список."""
        assert _SampleModel.de_list([], mock_client) == []

    def test_de_list_none(self, mock_client):
        """de_list(None) возвращает пустой список."""
        assert _SampleModel.de_list(None, mock_client) == []


class TestIsValidData:
    """Тесты is_dict_model_data / is_array_model_data."""

    def test_is_dict_model_data_valid(self):
        assert ZvukMusicModel.is_dict_model_data({"key": "val"})

    def test_is_dict_model_data_empty(self):
        assert not ZvukMusicModel.is_dict_model_data({})

    def test_is_dict_model_data_none(self):
        assert not ZvukMusicModel.is_dict_model_data(None)

    def test_is_array_model_data_valid(self):
        assert ZvukMusicModel.is_array_model_data([{"key": "val"}])

    def test_is_array_model_data_empty(self):
        assert not ZvukMusicModel.is_array_model_data([])

    def test_is_array_model_data_none(self):
        assert not ZvukMusicModel.is_array_model_data(None)
