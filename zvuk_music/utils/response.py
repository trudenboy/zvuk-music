"""GraphQL Response wrapper."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class Response(ZvukMusicModel):
    """API response wrapper.

    Supports both GraphQL format (with data field)
    and REST format (without wrapper).

    Attributes:
        data: Response data.
        errors: List of GraphQL errors.
        _raw_data: Original data (for REST API).

    Note (RU): Обёртка над ответом API.
    """

    client: Optional["ClientType"] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    _raw_data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.data,)

    @classmethod
    def de_json(cls, data: Any, client: Optional["ClientType"]) -> Optional["Response"]:
        """Deserialize API response.

        Args:
            data: Data dictionary from API.
            client: Client.

        Returns:
            Response object.

        Note (RU): Десериализация ответа API.
        """
        if data is None:
            return None

        if not isinstance(data, dict):
            return None

        # GraphQL format: {"data": {...}, "errors": [...]}
        if "data" in data:
            return cls(
                client=client,
                data=data.get("data"),
                errors=data.get("errors"),
                _raw_data=data,
            )

        # REST format (Tiny API): {"result": {...}} or just a dictionary
        return cls(
            client=client,
            data=data,  # Save entire response as data
            errors=None,
            _raw_data=data,
        )

    def has_errors(self) -> bool:
        """Check for errors in the response.

        Note (RU): Проверка наличия ошибок в ответе.
        """
        return bool(self.errors)

    def get_error(self) -> str:
        """Get the first error message.

        Note (RU): Получение текста первой ошибки.
        """
        if self.errors and len(self.errors) > 0:
            return str(self.errors[0].get("message", "Unknown GraphQL error"))
        return "Unknown error"

    def get_all_errors(self) -> List[str]:
        """Get all errors.

        Note (RU): Получение всех ошибок.
        """
        if not self.errors:
            return []
        return [e.get("message", str(e)) for e in self.errors]

    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get response data.

        Note (RU): Получение данных ответа.
        """
        return self.data
