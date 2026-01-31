####################################################
# THIS IS AUTO GENERATED COPY. DON'T EDIT BY HANDS #
####################################################

"""HTTP клиент для Zvuk Music API."""

import asyncio
import json
import keyword
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import aiofiles
import aiohttp

from zvuk_music.exceptions import (
    BadRequestError,
    BotDetectedError,
    GraphQLError,
    NetworkError,
    NotFoundError,
    TimedOutError,
    UnauthorizedError,
    ZvukMusicError,
)
from zvuk_music.utils.response import Response

if TYPE_CHECKING:
    from zvuk_music.base import ClientType, JSONType

API_URL = "https://zvuk.com/api/v1/graphql"
TINY_API_URL = "https://zvuk.com/api/tiny"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 10.0
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://zvuk.com/",
    "Origin": "https://zvuk.com",
}

_reserved_names = list(keyword.kwlist) + ["ClientType", "client"]

logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class _DefaultTimeout:
    """Заглушка для установки времени ожидания по умолчанию."""

    pass


default_timeout = _DefaultTimeout()
TimeoutType = Union[int, float, _DefaultTimeout]


class Request:
    """Вспомогательный класс для выполнения HTTP запросов.

    Предоставляет методы для выполнения POST и GET запросов,
    GraphQL запросов, скачивания файлов.

    Args:
        client: Клиент Zvuk Music.
        headers: Заголовки передаваемые с каждым запросом.
        proxy_url: URL прокси сервера.
        timeout: Таймаут запросов по умолчанию.
    """

    def __init__(
        self,
        client: Optional["ClientType"] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy_url: Optional[str] = None,
        timeout: "TimeoutType" = default_timeout,
    ) -> None:
        self.headers = DEFAULT_HEADERS.copy()
        if headers:
            self.headers.update(headers)
        self.headers.setdefault("Content-Type", "application/json")

        self._timeout = DEFAULT_TIMEOUT
        self.set_timeout(timeout)

        self.client: Optional["ClientType"] = None
        if client:
            self.set_and_return_client(client)

        # aiohttp
        self.proxy_url = proxy_url

        # requests
        self.proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

        self._user_agent = DEFAULT_USER_AGENT

    def set_timeout(self, timeout: Union[int, float, object] = default_timeout) -> None:
        """Устанавливает время ожидания для всех запросов.

        Args:
            timeout: Время ожидания от сервера в секундах.
        """
        if isinstance(timeout, _DefaultTimeout):
            self._timeout = DEFAULT_TIMEOUT
        else:
            self._timeout = float(timeout)  # type: ignore[arg-type]

    def set_user_agent(self, user_agent: str) -> None:
        """Устанавливает User-Agent для всех запросов.

        Args:
            user_agent: Строка User-Agent.
        """
        self._user_agent = user_agent

    def set_authorization(self, token: str) -> None:
        """Добавляет заголовок авторизации для каждого запроса.

        Args:
            token: Токен авторизации X-Auth-Token.
        """
        self.headers["X-Auth-Token"] = token

    def set_and_return_client(self, client: "ClientType") -> "ClientType":
        """Принимает клиент и присваивает его текущему объекту.

        При наличии токена добавляет заголовок авторизации.

        Args:
            client: Клиент Zvuk Music.

        Returns:
            Клиент Zvuk Music.
        """
        self.client = client

        if self.client and getattr(self.client, "token", None):
            self.set_authorization(self.client.token)

        return self.client

    @staticmethod
    def _convert_camel_to_snake(text: str) -> str:
        """Конвертация CamelCase в snake_case.

        Args:
            text: Название переменной в CamelCase.

        Returns:
            Название переменной в snake_case.
        """
        s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()

    @staticmethod
    def _object_hook(obj: "JSONType") -> "JSONType":
        """Нормализация имён переменных пришедших с API.

        Конвертирует CamelCase в snake_case, обрабатывает
        зарезервированные слова Python.

        Args:
            obj: Словарь данных от API.

        Returns:
            Словарь с нормализованными ключами.
        """
        if not isinstance(obj, dict):
            return obj

        cleaned_object: Dict[str, "JSONType"] = {}
        for key, value in obj.items():
            key = Request._convert_camel_to_snake(key.replace("-", "_"))
            key = key.lower()

            if key in _reserved_names:
                key += "_"

            if len(key) and key[0].isdigit():
                key = "_" + key

            cleaned_object[key] = value

        return cleaned_object

    def _parse(self, json_data: bytes) -> Optional[Response]:
        """Разбор ответа от API.

        Args:
            json_data: Ответ от API в байтах.

        Returns:
            Объект Response.

        Raises:
            ZvukMusicError: При ошибке парсинга.
            BotDetectedError: При обнаружении бот-защиты.
        """
        try:
            decoded_s = json_data.decode("UTF-8")

            # Проверка на бот-защиту
            if "bot activity" in decoded_s.lower() or "<html" in decoded_s.lower()[:100]:
                raise BotDetectedError(
                    "API detected bot activity. Try using a different User-Agent."
                )

            data = json.loads(decoded_s, object_hook=Request._object_hook)

        except UnicodeDecodeError as e:
            logger.debug("Logging raw invalid UTF-8 response:\n%r", json_data)
            raise ZvukMusicError("Server response could not be decoded using UTF-8") from e
        except json.JSONDecodeError as e:
            # Проверка HTML ответа (бот-защита)
            if b"<html" in json_data[:100].lower():
                raise BotDetectedError(
                    "API returned HTML instead of JSON. Bot protection detected."
                ) from e
            raise ZvukMusicError("Invalid server response (not JSON)") from e

        return Response.de_json(data, self.client)

    async def _request_wrapper(self, *args: Any, **kwargs: Any) -> bytes:
        """Обёртка над запросом библиотеки requests.

        Добавляет необходимые заголовки, обрабатывает статус коды,
        следит за таймаутом, кидает необходимые исключения.

        Args:
            *args: Аргументы для aiohttp.request.
            **kwargs: Ключевые аргументы для aiohttp.request.

        Returns:
            Тело ответа в байтах.

        Raises:
            TimedOutError: При превышении времени ожидания.
            UnauthorizedError: При невалидном токене.
            BadRequestError: При неправильном запросе.
            NotFoundError: При отсутствии ресурса.
            NetworkError: При проблемах с сетью.
        """
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        kwargs["headers"]["User-Agent"] = self._user_agent
        kwargs["headers"].update(self.headers)

        if kwargs.get("timeout") is default_timeout or kwargs.get("timeout") is None:
            kwargs["timeout"] = aiohttp.ClientTimeout(total=self._timeout)
        else:
            kwargs["timeout"] = aiohttp.ClientTimeout(total=kwargs["timeout"])

        try:
            async with aiohttp.request(*args, **kwargs) as _resp:
                resp = _resp
                content = await resp.read()
        except asyncio.TimeoutError as e:
            raise TimedOutError("Request timed out") from e
        except aiohttp.ClientError as e:
            raise NetworkError(str(e)) from e

        if 200 <= resp.status <= 299:
            return bytes(content)

        message = "Unknown error"
        try:
            parse = self._parse(content)
            if parse:
                message = parse.get_error()
        except ZvukMusicError:
            message = "Unknown HTTPError"

        if resp.status in (401, 403):
            raise UnauthorizedError(message)
        if resp.status == 400:
            raise BadRequestError(message)
        if resp.status == 404:
            raise NotFoundError(message)
        if resp.status in (409, 413):
            raise NetworkError(message)
        if resp.status == 502:
            raise NetworkError("Bad Gateway")

        raise NetworkError(f"{message} ({resp.status}): {content!r}")

    async def graphql(
        self,
        query: str,
        operation_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
    ) -> Dict[str, Any]:
        """Выполнение GraphQL запроса.

        Args:
            query: GraphQL запрос.
            operation_name: Имя операции (опционально).
            variables: Переменные запроса.
            timeout: Таймаут запроса.

        Returns:
            Данные ответа.

        Raises:
            GraphQLError: При ошибке GraphQL.
        """
        payload: Dict[str, Any] = {"query": query}

        if operation_name:
            payload["operationName"] = operation_name

        if variables:
            payload["variables"] = variables

        result = await self._request_wrapper(
            "POST",
            API_URL,
            json=payload,
            proxy=self.proxy_url,
            timeout=timeout,
        )

        response = self._parse(result)

        if response and response.has_errors():
            raise GraphQLError(
                "GraphQL request failed",
                errors=response.errors,
            )

        if response:
            return response.get_result() or {}

        return {}

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Отправка GET запроса.

        Args:
            url: Адрес для запроса.
            params: GET параметры.
            timeout: Таймаут запроса.
            **kwargs: Дополнительные аргументы для requests.

        Returns:
            Данные ответа.
        """
        result = await self._request_wrapper(
            "GET",
            url,
            params=params,
            proxy=self.proxy_url,
            timeout=timeout,
            **kwargs,
        )
        response = self._parse(result)
        if response:
            data = response.get_result()
            # Tiny API возвращает {"result": {...}}
            if isinstance(data, dict) and "result" in data:
                inner: Optional[Dict[str, Any]] = data["result"]
                return inner
            return data

        return None

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Отправка POST запроса.

        Args:
            url: Адрес для запроса.
            data: POST тело запроса.
            timeout: Таймаут запроса.
            **kwargs: Дополнительные аргументы для requests.

        Returns:
            Данные ответа.
        """
        result = await self._request_wrapper(
            "POST",
            url,
            json=data,
            proxy=self.proxy_url,
            timeout=timeout,
            **kwargs,
        )
        response = self._parse(result)
        if response:
            return response.get_result()

        return None

    async def retrieve(
        self,
        url: str,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> bytes:
        """GET запрос и получение сырых данных.

        Args:
            url: Адрес для запроса.
            timeout: Таймаут запроса.
            **kwargs: Дополнительные аргументы для requests.

        Returns:
            Тело ответа в байтах.
        """
        return await self._request_wrapper(
            "GET",
            url,
            proxy=self.proxy_url,
            timeout=timeout,
            **kwargs,
        )

    async def download(
        self,
        url: str,
        filename: str,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> None:
        """Скачивание файла.

        Args:
            url: Адрес для скачивания.
            filename: Путь для сохранения файла.
            timeout: Таймаут запроса.
            **kwargs: Дополнительные аргументы для requests.
        """
        result = await self.retrieve(url, timeout=timeout, **kwargs)
        async with aiofiles.open(filename, "wb") as f:
            await f.write(result)
