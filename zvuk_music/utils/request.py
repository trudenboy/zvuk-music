"""HTTP client for Zvuk Music API.

Note (RU): HTTP клиент для Zvuk Music API.
"""

import json
import keyword
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import requests

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
    """Stub for setting default timeout.

    Note (RU): Заглушка для установки времени ожидания по умолчанию.
    """

    pass


default_timeout = _DefaultTimeout()
TimeoutType = Union[int, float, _DefaultTimeout]


class Request:
    """Helper class for making HTTP requests.

    Provides methods for making POST and GET requests,
    GraphQL queries, and file downloads.

    Args:
        client: Zvuk Music client.
        headers: Headers sent with every request.
        proxy_url: Proxy server URL.
        timeout: Default request timeout.

    Note (RU): Вспомогательный класс для выполнения HTTP запросов.
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
        """Set timeout for all requests.

        Args:
            timeout: Server response timeout in seconds.

        Note (RU): Устанавливает время ожидания для всех запросов.
        """
        if isinstance(timeout, _DefaultTimeout):
            self._timeout = DEFAULT_TIMEOUT
        else:
            self._timeout = float(timeout)  # type: ignore[arg-type]

    def set_user_agent(self, user_agent: str) -> None:
        """Set User-Agent for all requests.

        Args:
            user_agent: User-Agent string.

        Note (RU): Устанавливает User-Agent для всех запросов.
        """
        self._user_agent = user_agent

    def set_authorization(self, token: str) -> None:
        """Add authorization header to every request.

        Args:
            token: X-Auth-Token authorization token.

        Note (RU): Добавляет заголовок авторизации для каждого запроса.
        """
        self.headers["X-Auth-Token"] = token

    def set_and_return_client(self, client: "ClientType") -> "ClientType":
        """Accept a client and assign it to the current object.

        Adds authorization header if token is present.

        Args:
            client: Zvuk Music client.

        Returns:
            Zvuk Music client.

        Note (RU): Принимает клиент и присваивает его текущему объекту.
        """
        self.client = client

        if self.client and getattr(self.client, "token", None):
            self.set_authorization(self.client.token)

        return self.client

    @staticmethod
    def _convert_camel_to_snake(text: str) -> str:
        """Convert CamelCase to snake_case.

        Args:
            text: Variable name in CamelCase.

        Returns:
            Variable name in snake_case.

        Note (RU): Конвертация CamelCase в snake_case.
        """
        s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()

    @staticmethod
    def _object_hook(obj: "JSONType") -> "JSONType":
        """Normalize variable names from the API.

        Converts CamelCase to snake_case, handles Python reserved words.

        Args:
            obj: Data dictionary from API.

        Returns:
            Dictionary with normalized keys.

        Note (RU): Нормализация имён переменных пришедших с API.
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
        """Parse API response.

        Args:
            json_data: API response in bytes.

        Returns:
            Response object.

        Raises:
            ZvukMusicError: On parsing error.
            BotDetectedError: On bot protection detection.

        Note (RU): Разбор ответа от API.
        """
        try:
            decoded_s = json_data.decode("UTF-8")

            # Check for bot protection
            if "bot activity" in decoded_s.lower() or "<html" in decoded_s.lower()[:100]:
                raise BotDetectedError(
                    "API detected bot activity. Try using a different User-Agent."
                )

            data = json.loads(decoded_s, object_hook=Request._object_hook)

        except UnicodeDecodeError as e:
            logger.debug("Logging raw invalid UTF-8 response:\n%r", json_data)
            raise ZvukMusicError("Server response could not be decoded using UTF-8") from e
        except json.JSONDecodeError as e:
            # Check HTML response (bot protection)
            if b"<html" in json_data[:100].lower():
                raise BotDetectedError(
                    "API returned HTML instead of JSON. Bot protection detected."
                ) from e
            raise ZvukMusicError("Invalid server response (not JSON)") from e

        return Response.de_json(data, self.client)

    def _request_wrapper(self, *args: Any, **kwargs: Any) -> bytes:
        """Wrapper around the requests library.

        Adds necessary headers, handles status codes,
        monitors timeout, raises appropriate exceptions.

        Args:
            *args: Arguments for requests.request.
            **kwargs: Keyword arguments for requests.request.

        Returns:
            Response body in bytes.

        Raises:
            TimedOutError: On timeout.
            UnauthorizedError: On invalid token.
            BadRequestError: On bad request.
            NotFoundError: On missing resource.
            NetworkError: On network issues.

        Note (RU): Обёртка над запросом библиотеки requests.
        """
        if "headers" not in kwargs:
            kwargs["headers"] = {}

        kwargs["headers"]["User-Agent"] = self._user_agent
        kwargs["headers"].update(self.headers)

        if kwargs.get("timeout") is default_timeout or kwargs.get("timeout") is None:
            kwargs["timeout"] = self._timeout

        try:
            resp = requests.request(*args, **kwargs)
        except requests.Timeout as e:
            raise TimedOutError("Request timed out") from e
        except requests.RequestException as e:
            raise NetworkError(str(e)) from e

        if 200 <= resp.status_code <= 299:
            return bytes(resp.content)

        message = "Unknown error"
        try:
            parse = self._parse(resp.content)
            if parse:
                message = parse.get_error()
        except ZvukMusicError:
            message = "Unknown HTTPError"

        if resp.status_code in (401, 403):
            raise UnauthorizedError(message)
        if resp.status_code == 400:
            raise BadRequestError(message)
        if resp.status_code == 404:
            raise NotFoundError(message)
        if resp.status_code in (409, 413):
            raise NetworkError(message)
        if resp.status_code == 502:
            raise NetworkError("Bad Gateway")

        raise NetworkError(f"{message} ({resp.status_code}): {resp.content!r}")

    def graphql(
        self,
        query: str,
        operation_name: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
    ) -> Dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query.
            operation_name: Operation name (optional).
            variables: Query variables.
            timeout: Request timeout.

        Returns:
            Response data.

        Raises:
            GraphQLError: On GraphQL error.

        Note (RU): Выполнение GraphQL запроса.
        """
        payload: Dict[str, Any] = {"query": query}

        if operation_name:
            payload["operationName"] = operation_name

        if variables:
            payload["variables"] = variables

        result = self._request_wrapper(
            "POST",
            API_URL,
            json=payload,
            proxies=self.proxies,
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

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Send a GET request.

        Args:
            url: Request URL.
            params: GET parameters.
            timeout: Request timeout.
            **kwargs: Additional arguments for requests.

        Returns:
            Response data.

        Note (RU): Отправка GET запроса.
        """
        result = self._request_wrapper(
            "GET",
            url,
            params=params,
            proxies=self.proxies,
            timeout=timeout,
            **kwargs,
        )
        response = self._parse(result)
        if response:
            data = response.get_result()
            # Tiny API returns {"result": {...}}
            if isinstance(data, dict) and "result" in data:
                inner: Optional[Dict[str, Any]] = data["result"]
                return inner
            return data

        return None

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Send a POST request.

        Args:
            url: Request URL.
            data: POST request body.
            timeout: Request timeout.
            **kwargs: Additional arguments for requests.

        Returns:
            Response data.

        Note (RU): Отправка POST запроса.
        """
        result = self._request_wrapper(
            "POST",
            url,
            json=data,
            proxies=self.proxies,
            timeout=timeout,
            **kwargs,
        )
        response = self._parse(result)
        if response:
            return response.get_result()

        return None

    def retrieve(
        self,
        url: str,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> bytes:
        """GET request returning raw data.

        Args:
            url: Request URL.
            timeout: Request timeout.
            **kwargs: Additional arguments for requests.

        Returns:
            Response body in bytes.

        Note (RU): GET запрос и получение сырых данных.
        """
        return self._request_wrapper(
            "GET",
            url,
            proxies=self.proxies,
            timeout=timeout,
            **kwargs,
        )

    def download(
        self,
        url: str,
        filename: str,
        timeout: "TimeoutType" = default_timeout,
        **kwargs: Any,
    ) -> None:
        """Download a file.

        Args:
            url: Download URL.
            filename: File save path.
            timeout: Request timeout.
            **kwargs: Additional arguments for requests.

        Note (RU): Скачивание файла.
        """
        result = self.retrieve(url, timeout=timeout, **kwargs)
        with open(filename, "wb") as f:
            f.write(result)
