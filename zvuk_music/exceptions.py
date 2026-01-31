"""Exceptions for the Zvuk Music API library.

Note (RU): Исключения библиотеки Zvuk Music API.
"""

from typing import Any, Optional


class ZvukMusicError(Exception):
    """Base exception for the library.

    Note (RU): Базовое исключение библиотеки.
    """

    def __init__(self, message: str = "", *args: Any) -> None:
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        return self.message


class NetworkError(ZvukMusicError):
    """Network error during request execution.

    Note (RU): Сетевая ошибка при выполнении запроса.
    """

    pass


class TimedOutError(NetworkError):
    """Request timed out.

    Note (RU): Превышено время ожидания запроса.
    """

    pass


class BadRequestError(ZvukMusicError):
    """Bad request (HTTP 400).

    Note (RU): Некорректный запрос (HTTP 400).
    """

    pass


class UnauthorizedError(ZvukMusicError):
    """Authorization error (HTTP 401/403 or invalid token).

    Note (RU): Ошибка авторизации (HTTP 401/403 или невалидный токен).
    """

    pass


class NotFoundError(ZvukMusicError):
    """Resource not found (HTTP 404).

    Note (RU): Ресурс не найден (HTTP 404).
    """

    pass


class GraphQLError(ZvukMusicError):
    """GraphQL query error.

    Note (RU): Ошибка GraphQL запроса.
    """

    def __init__(
        self,
        message: str = "",
        errors: Optional[list[dict[str, Any]]] = None,
        *args: Any,
    ) -> None:
        self.errors = errors or []
        super().__init__(message, *args)

    def __str__(self) -> str:
        if self.errors:
            error_messages = [e.get("message", str(e)) for e in self.errors]
            return f"{self.message}: {'; '.join(error_messages)}"
        return self.message


class SubscriptionRequiredError(ZvukMusicError):
    """Subscription required for content access (high/flac quality).

    Note (RU): Требуется подписка для доступа к контенту (high/flac качество).
    """

    pass


class QualityNotAvailableError(ZvukMusicError):
    """Requested audio quality is not available.

    Note (RU): Запрошенное качество аудио недоступно.
    """

    pass


class BotDetectedError(ZvukMusicError):
    """API detected bot activity and blocked the request.

    Note (RU): API обнаружил бот-активность и заблокировал запрос.
    """

    pass
