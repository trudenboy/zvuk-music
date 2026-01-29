"""Тесты модели Profile."""

import pytest

from zvuk_music.models.profile import Profile, ProfileResult


class TestProfileResult:
    """Тесты ProfileResult."""

    def test_de_json_valid(self, mock_client, sample_profile_data):
        """Тест десериализации валидных данных."""
        result = ProfileResult.de_json(sample_profile_data, mock_client)

        assert result is not None
        assert result.id == 123456789
        assert result.token == "test_token_123"
        assert result.is_anonymous is True
        assert result.allow_explicit is True

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        result = ProfileResult.de_json(None, mock_client)
        assert result is None

    def test_is_authorized_anonymous(self, mock_client, sample_profile_data):
        """Тест проверки авторизации для анонимного пользователя."""
        result = ProfileResult.de_json(sample_profile_data, mock_client)
        assert result.is_authorized() is False

    def test_is_authorized_registered(self, mock_client, sample_profile_data):
        """Тест проверки авторизации для зарегистрированного пользователя."""
        sample_profile_data["is_anonymous"] = False
        result = ProfileResult.de_json(sample_profile_data, mock_client)
        assert result.is_authorized() is True


class TestProfile:
    """Тесты Profile."""

    def test_de_json_valid(self, mock_client, sample_profile_data):
        """Тест десериализации валидных данных."""
        data = {"result": sample_profile_data}
        profile = Profile.de_json(data, mock_client)

        assert profile is not None
        assert profile.result is not None
        assert profile.result.id == 123456789

    def test_de_json_none(self, mock_client):
        """Тест десериализации None."""
        profile = Profile.de_json(None, mock_client)
        assert profile is None

    def test_is_authorized(self, mock_client, sample_profile_data):
        """Тест проверки авторизации через Profile."""
        data = {"result": sample_profile_data}
        profile = Profile.de_json(data, mock_client)
        assert profile.is_authorized() is False

    def test_token_property(self, mock_client, sample_profile_data):
        """Тест получения токена через свойство."""
        data = {"result": sample_profile_data}
        profile = Profile.de_json(data, mock_client)
        assert profile.token == "test_token_123"

    def test_token_property_no_result(self, mock_client):
        """Тест получения токена когда result отсутствует."""
        data = {"result": None}
        profile = Profile.de_json(data, mock_client)
        assert profile.token == ""
