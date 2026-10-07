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
