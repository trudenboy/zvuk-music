"""Base classes for the Zvuk Music API library.

Note (RU): Базовые классы библиотеки Zvuk Music API.
"""

import dataclasses
import keyword
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Sequence, Tuple, Union, cast

from typing_extensions import Self, TypeGuard

from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music import Client, ClientAsync

try:
    import ujson as json

    _ujson = True
except ImportError:
    import json  # type: ignore[no-redef]

    _ujson = False

_reserved_names = keyword.kwlist

logger = logging.getLogger(__name__)

JSONType = Union[Dict[str, "JSONType"], Sequence["JSONType"], str, int, float, bool, None]
ClientType = Union["Client", "ClientAsync"]
ModelFieldType = Union[
    Dict[str, "ModelFieldType"],
    Sequence["ModelFieldType"],
    "ZvukMusicModel",
    str,
    int,
    float,
    bool,
    None,
]
ModelFieldMap = Dict[str, "ModelFieldType"]
MapTypeToDeJson = Dict[str, Callable[["JSONType", "ClientType"], Optional["ZvukMusicModel"]]]


class ZvukMusicObject:
    """Base class for all library classes.

    Note (RU): Базовый класс для всех классов библиотеки.
    """

    pass


@model
class ZvukMusicModel(ZvukMusicObject):
    """Base class for all library models.

    Provides methods for serialization/deserialization of objects
    from/to JSON and dictionaries.

    Note (RU): Базовый класс для всех моделей библиотеки.
    Предоставляет методы для сериализации/десериализации объектов
    из/в JSON и словари.
    """

    client: Optional["ClientType"] = None

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item: str) -> Any:
        return self.__dict__[item]

    @staticmethod
    def report_unknown_fields_callback(klass: type, unknown_fields: JSONType) -> None:
        """Callback for handling unknown fields.

        Note (RU): Обратный вызов для обработки неизвестных полей.
        """
        logger.warning(
            "Found unknown fields received from API! "
            "Please report this at https://github.com/your-repo/zvuk-api/issues"
        )
        logger.warning(f"Type: {klass.__module__}.{klass.__name__}; fields: {unknown_fields}")

    @staticmethod
    def is_dict_model_data(data: JSONType) -> TypeGuard[Dict[str, Any]]:
        """Check if data is a valid dictionary.

        Args:
            data: Data to validate.

        Returns:
            Whether the data is valid.

        Note (RU): Проверка на соответствие данных словарю.
        """
        return bool(data) and isinstance(data, dict)

    @staticmethod
    def valid_client(client: Optional["ClientType"]) -> TypeGuard["Client"]:
        """Check that the client is provided and is synchronous.

        Args:
            client: Client to check.

        Returns:
            Whether the client is synchronous.

        Note (RU): Проверка что клиент передан и является синхронным.
        """
        from zvuk_music import Client

        return isinstance(client, Client)

    @staticmethod
    def valid_async_client(client: Optional["ClientType"]) -> TypeGuard["ClientAsync"]:
        """Check that the client is provided and is asynchronous.

        Args:
            client: Client to check.

        Returns:
            Whether the client is asynchronous.

        Note (RU): Проверка что клиент передан и является асинхронным.
        """
        from zvuk_music import ClientAsync

        return isinstance(client, ClientAsync)

    @staticmethod
    def is_array_model_data(data: JSONType) -> TypeGuard[List[Dict[str, Any]]]:
        """Check if data is a valid list of dictionaries.

        Args:
            data: Data to validate.

        Returns:
            Whether the data is valid.

        Note (RU): Проверка на соответствие данных массиву словарей.
        """
        return (
            bool(data) and isinstance(data, list) and all(isinstance(item, dict) for item in data)
        )

    @classmethod
    def cleanup_data(cls, data: JSONType, client: Optional["ClientType"]) -> Dict[str, Any]:
        """Remove undeclared fields for the current model from raw data.

        Note:
            Only filters a field:value dictionary. Otherwise returns an empty dict.

        Args:
            data: Fields and values of the object being deserialized.
            client: Zvuk Music client.

        Returns:
            Filtered data.

        Note (RU): Удаляет незадекларированные поля для текущей модели из сырых данных.
        """
        if not ZvukMusicModel.is_dict_model_data(data):
            return {}

        data = data.copy()

        fields = {f.name for f in dataclasses.fields(cls)}

        cleaned_data: Dict[str, JSONType] = {}
        unknown_data: Dict[str, JSONType] = {}

        for k, v in data.items():
            if k in fields:
                cleaned_data[k] = v
            else:
                unknown_data[k] = v

        if client and getattr(client, "report_unknown_fields", False) and unknown_data:
            cls.report_unknown_fields_callback(cls, unknown_data)

        return cleaned_data

    @classmethod
    def de_json(cls, data: "JSONType", client: "ClientType") -> Optional[Self]:
        """Deserialize an object.

        Note:
            Overridden in subclasses when there are nested objects.

        Args:
            data: Fields and values of the object being deserialized.
            client: Zvuk Music client.

        Returns:
            Deserialized object.

        Note (RU): Десериализация объекта.
        """
        if not cls.is_dict_model_data(data):
            return None

        return cls(client=client, **cls.cleanup_data(data, client))

    @classmethod
    def de_list(cls, data: JSONType, client: "ClientType") -> List[Self]:
        """Deserialize a list of objects.

        Note:
            Overridden in subclasses if necessary.

        Args:
            data: List of dictionaries with fields and values of the object being deserialized.
            client: Zvuk Music client.

        Returns:
            List of deserialized objects.

        Note (RU): Десериализация списка объектов.
        """
        if not cls.is_array_model_data(data):
            return []

        items = [cls.de_json(item, client) for item in data]
        return [item for item in items if item is not None]

    def to_json(self, for_request: bool = False) -> str:
        """Serialize the object to a JSON string.

        Args:
            for_request: Whether to prepare the object for sending in a request body.

        Returns:
            JSON-serialized object.

        Note (RU): Сериализация объекта в JSON строку.
        """
        result: str = json.dumps(self.to_dict(for_request), ensure_ascii=not _ujson)
        return result

    def to_dict(self, for_request: bool = False) -> JSONType:
        """Recursively serialize the object to a dictionary.

        Args:
            for_request: Whether to convert all fields back to camelCase.

        Note:
            Excludes ``client`` and ``_id_attrs`` from serialization.

        Returns:
            Dictionary-serialized object.

        Note (RU): Рекурсивная сериализация объекта в словарь.
        """

        def parse(val: Union["ZvukMusicModel", JSONType]) -> JSONType:
            if isinstance(val, ZvukMusicModel):
                return val.to_dict(for_request)
            if isinstance(val, list):
                return [parse(it) for it in val]
            if isinstance(val, dict):
                return {key: parse(value) for key, value in val.items()}
            return val

        data = self.__dict__.copy()
        data.pop("client", None)
        data.pop("_id_attrs", None)

        if for_request:
            for k, v in data.copy().items():
                camel_case = "".join(word.title() for word in k.split("_"))
                camel_case = camel_case[0].lower() + camel_case[1:]

                data.pop(k)
                data.update({camel_case: v})
        else:
            for k, v in data.copy().items():
                if k.lower() in _reserved_names:
                    data.pop(k)
                    data.update({f"{k}_": v})

        return parse(data)

    def _get_id_attrs(self) -> Tuple[str, ...]:
        """Get key attributes of the object.

        Returns:
            Key attributes of the object for comparison.

        Note (RU): Получение ключевых атрибутов объекта.
        """
        return cast(Tuple[str, ...], getattr(self, "_id_attrs", ()))

    def __eq__(self, other: Any) -> bool:
        """Check equality of two objects.

        Note:
            Comparison is based on attributes listed in ``_id_attrs``.

        Returns:
            Whether the objects are equal (by content).

        Note (RU): Проверка на равенство двух объектов.
        """
        if isinstance(other, self.__class__):
            return self._get_id_attrs() == other._get_id_attrs()
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Hash function implementation based on key attributes.

        Returns:
            Hash of the object.

        Note (RU): Реализация хеш-функции на основе ключевых атрибутов.
        """
        id_attrs = self._get_id_attrs()
        if not id_attrs:
            return super().__hash__()

        frozen_attrs = tuple(
            frozenset(attr) if isinstance(attr, list) else attr for attr in id_attrs
        )
        return hash((self.__class__, frozen_attrs))
