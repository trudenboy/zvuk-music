"""Tests for base classes."""

import json

import pytest

from zvuk_music.base import ZvukMusicModel
from zvuk_music.models.common import Genre
from zvuk_music.utils import model


@model
class _SampleModel(ZvukMusicModel):
    """Test model."""

    id: str = ""
    name: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)


class TestCleanupData:
    """Tests for cleanup_data."""

    def test_extra_fields_filtered(self, mock_client):
        """Unknown fields are filtered out."""
        data = {"id": "1", "name": "test", "unknown_field": "value", "another": 42}
        cleaned = _SampleModel.cleanup_data(data, mock_client)
        assert "id" in cleaned
        assert "name" in cleaned
        assert "unknown_field" not in cleaned
        assert "another" not in cleaned

    def test_report_unknown_fields(self, mock_client):
        """report_unknown_fields triggers callback on unknown fields."""
        mock_client.report_unknown_fields = True
        data = {"id": "1", "name": "test", "extra": "val"}

        # Should not raise an error
        cleaned = _SampleModel.cleanup_data(data, mock_client)
        assert "extra" not in cleaned
        mock_client.report_unknown_fields = False

    def test_none_data_returns_empty(self, mock_client):
        """None returns an empty dictionary."""
        assert _SampleModel.cleanup_data(None, mock_client) == {}

    def test_empty_dict_returns_empty(self, mock_client):
        """Empty dictionary returns an empty dictionary."""
        assert _SampleModel.cleanup_data({}, mock_client) == {}


class TestToDict:
    """Tests for to_dict."""

    def test_excludes_client(self, mock_client):
        """client is not included in to_dict()."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        d = obj.to_dict()
        assert "client" not in d
        assert d["id"] == "1"
        assert d["name"] == "test"

    def test_excludes_id_attrs(self, mock_client):
        """_id_attrs is not included in to_dict()."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        d = obj.to_dict()
        assert "_id_attrs" not in d

    def test_for_request_camel_case(self, mock_client):
        """to_dict(for_request=True) converts keys to camelCase."""
        genre = Genre(client=mock_client, id="1", name="Rock", short_name="rock")
        d = genre.to_dict(for_request=True)
        assert "shortName" in d
        assert "short_name" not in d

    def test_nested_models(self, mock_client):
        """to_dict recursively serializes nested models."""
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
    """Tests for to_json."""

    def test_returns_valid_json(self, mock_client):
        """to_json() returns valid JSON."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        json_str = obj.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == "1"
        assert parsed["name"] == "test"
        assert "client" not in parsed


class TestEquality:
    """Tests for __eq__."""

    def test_equality_by_id_attrs(self, mock_client):
        """__eq__ compares by _id_attrs."""
        obj1 = _SampleModel(client=mock_client, id="1", name="name1")
        obj2 = _SampleModel(client=mock_client, id="1", name="name2")
        assert obj1 == obj2

    def test_inequality_by_id_attrs(self, mock_client):
        """Different _id_attrs means unequal objects."""
        obj1 = _SampleModel(client=mock_client, id="1", name="test")
        obj2 = _SampleModel(client=mock_client, id="2", name="test")
        assert obj1 != obj2

    def test_inequality_different_type(self, mock_client):
        """Different types are not equal."""
        obj = _SampleModel(client=mock_client, id="1", name="test")
        assert obj != "not a model"


class TestHash:
    """Tests for __hash__."""

    def test_hash_by_id_attrs(self, mock_client):
        """__hash__ is stable for the same id."""
        obj1 = _SampleModel(client=mock_client, id="1", name="name1")
        obj2 = _SampleModel(client=mock_client, id="1", name="name2")
        assert hash(obj1) == hash(obj2)

    def test_hash_different_id(self, mock_client):
        """Different ids produce different hashes (usually)."""
        obj1 = _SampleModel(client=mock_client, id="1", name="test")
        obj2 = _SampleModel(client=mock_client, id="2", name="test")
        # Different ids usually produce different hashes
        assert hash(obj1) != hash(obj2)

    def test_usable_in_set(self, mock_client):
        """Objects can be used in a set."""
        obj1 = _SampleModel(client=mock_client, id="1", name="a")
        obj2 = _SampleModel(client=mock_client, id="1", name="b")
        obj3 = _SampleModel(client=mock_client, id="2", name="c")
        s = {obj1, obj2, obj3}
        assert len(s) == 2


class TestDeJson:
    """Tests for base de_json."""

    def test_de_json_valid(self, mock_client):
        """Base de_json works."""
        obj = _SampleModel.de_json({"id": "1", "name": "test"}, mock_client)
        assert obj is not None
        assert obj.id == "1"

    def test_de_json_none(self, mock_client):
        """de_json(None) returns None."""
        assert _SampleModel.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        """de_json({}) returns None."""
        assert _SampleModel.de_json({}, mock_client) is None

    def test_de_list_valid(self, mock_client):
        """de_list works with a list."""
        data = [{"id": "1", "name": "a"}, {"id": "2", "name": "b"}]
        items = _SampleModel.de_list(data, mock_client)
        assert len(items) == 2

    def test_de_list_empty(self, mock_client):
        """de_list([]) returns an empty list."""
        assert _SampleModel.de_list([], mock_client) == []

    def test_de_list_none(self, mock_client):
        """de_list(None) returns an empty list."""
        assert _SampleModel.de_list(None, mock_client) == []


class TestIsValidData:
    """Tests for is_dict_model_data / is_array_model_data."""

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
