"""GraphQL Response wrapper."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class Response(ZvukMusicModel):
    """Обёртка над ответом API.

    Поддерживает как GraphQL формат (с полем data),
    так и REST формат (без обёртки).

    Attributes:
        data: Данные ответа.
        errors: Список ошибок GraphQL.
        _raw_data: Исходные данные (для REST API).
    """

    client: Optional["ClientType"] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    _raw_data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.data,)

    @classmethod
    def de_json(cls, data: Any, client: Optional["ClientType"]) -> Optional["Response"]:
        """Десериализация ответа API.

        Args:
            data: Словарь данных от API.
            client: Клиент.

        Returns:
            Объект Response.
        """
        if data is None:
            return None

        if not isinstance(data, dict):
            return None

        # GraphQL формат: {"data": {...}, "errors": [...]}
        if "data" in data:
            return cls(
                client=client,
                data=data.get("data"),
                errors=data.get("errors"),
                _raw_data=data,
            )

        # REST формат (Tiny API): {"result": {...}} или просто словарь
        return cls(
            client=client,
            data=data,  # Сохраняем весь ответ как data
            errors=None,
            _raw_data=data,
        )

    def has_errors(self) -> bool:
        """Проверка наличия ошибок в ответе."""
        return bool(self.errors)

    def get_error(self) -> str:
        """Получение текста первой ошибки."""
        if self.errors and len(self.errors) > 0:
            return str(self.errors[0].get("message", "Unknown GraphQL error"))
        return "Unknown error"

    def get_all_errors(self) -> List[str]:
        """Получение всех ошибок."""
        if not self.errors:
            return []
        return [e.get("message", str(e)) for e in self.errors]

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Получение данных ответа."""
        return self.data
