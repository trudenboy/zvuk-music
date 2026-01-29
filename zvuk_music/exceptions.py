"""Исключения библиотеки Zvuk Music API."""

from typing import Any, Optional


class ZvukMusicError(Exception):
    """Базовое исключение библиотеки."""

    def __init__(self, message: str = "", *args: Any) -> None:
        self.message = message
        super().__init__(message, *args)

    def __str__(self) -> str:
        return self.message


class NetworkError(ZvukMusicError):
    """Сетевая ошибка при выполнении запроса."""

    pass


class TimedOutError(NetworkError):
    """Превышено время ожидания запроса."""

    pass


class BadRequestError(ZvukMusicError):
    """Некорректный запрос (HTTP 400)."""

    pass


class UnauthorizedError(ZvukMusicError):
    """Ошибка авторизации (HTTP 401/403 или невалидный токен)."""

    pass


class NotFoundError(ZvukMusicError):
    """Ресурс не найден (HTTP 404)."""

    pass


class GraphQLError(ZvukMusicError):
    """Ошибка GraphQL запроса."""

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
    """Требуется подписка для доступа к контенту (high/flac качество)."""

    pass


class QualityNotAvailableError(ZvukMusicError):
    """Запрошенное качество аудио недоступно."""

    pass


class BotDetectedError(ZvukMusicError):
    """API обнаружил бот-активность и заблокировал запрос."""

    pass
