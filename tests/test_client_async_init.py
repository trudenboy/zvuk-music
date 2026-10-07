"""Тесты инициализации асинхронного клиента."""

from unittest.mock import AsyncMock, patch

import pytest

from zvuk_music import ClientAsync
from zvuk_music.exceptions import BotDetectedError, UnauthorizedError


@pytest.fixture
def async_client():
    """Асинхронный клиент с замоканными _request.get() и _request.graphql()."""
    with patch.object(ClientAsync, "get_anonymous_token", return_value="test_token"):
        client = ClientAsync(token="test_token")
    client._request.get = AsyncMock()
    client._request.graphql = AsyncMock()
    return client


async def test_init_falls_back_to_graphql_when_profile_blocked(async_client):
    """init() проверяет токен через GraphQL, если tiny /profile заблокирован."""
    async_client._request.get.side_effect = BotDetectedError("blocked")
    async_client._request.graphql.return_value = {"collection": {}}
    result = await async_client.init()
    assert result is async_client
    assert await async_client.is_authorized() is True
    async_client._request.graphql.assert_awaited_once()


async def test_init_blocked_profile_with_invalid_token_raises(async_client):
    """init() пробрасывает UnauthorizedError, если GraphQL отклонил токен."""
    async_client._request.get.side_effect = BotDetectedError("blocked")
    async_client._request.graphql.side_effect = UnauthorizedError("bad")
    with pytest.raises(UnauthorizedError):
        await async_client.init()


async def test_update_playlist_keeps_current_name_and_visibility(async_client):
    """Async update_playlist подставляет текущие имя и видимость плейлиста."""
    async_client._request.graphql.side_effect = [
        {"get_playlists": [{"id": "1", "title": "My list", "is_public": True}]},
        {"playlist": {"update": True}},
    ]
    assert await async_client.update_playlist("1", ["t1"]) is True
    variables = async_client._request.graphql.await_args_list[-1].args[2]
    assert variables["name"] == "My list"
    assert variables["isPublic"] is True


async def test_profile_property_is_not_a_coroutine(async_client):
    """profile в async-клиенте — обычное свойство."""
    async_client._request.get.return_value = {"id": 7, "token": "t", "is_anonymous": False}
    await async_client.init()
    assert str(async_client.profile.id) == "7"
