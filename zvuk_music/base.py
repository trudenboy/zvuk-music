"""Базовые классы библиотеки Zvuk Music API."""

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
    Dict[str, "ModelFieldType"], Sequence["ModelFieldType"], "ZvukMusicModel", str, int, float, bool, None
]
ModelFieldMap = Dict[str, "ModelFieldType"]
MapTypeToDeJson = Dict[str, Callable[["JSONType", "ClientType"], Optional["ZvukMusicModel"]]]


class ZvukMusicObject:
    """Базовый класс для всех классов библиотеки."""

    pass


@model
class ZvukMusicModel(ZvukMusicObject):
    """Базовый класс для всех моделей библиотеки.

    Предоставляет методы для сериализации/десериализации объектов
    из/в JSON и словари.
    """

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item: str) -> Any:
        return self.__dict__[item]

    @staticmethod
    def report_unknown_fields_callback(klass: type, unknown_fields: JSONType) -> None:
        """Обратный вызов для обработки неизвестных полей."""
        logger.warning(
            "Found unknown fields received from API! "
            "Please report this at https://github.com/your-repo/zvuk-api/issues"
        )
        logger.warning(f"Type: {klass.__module__}.{klass.__name__}; fields: {unknown_fields}")

    @staticmethod
    def is_dict_model_data(data: JSONType) -> TypeGuard[Dict[str, JSONType]]:
        """Проверка на соответствие данных словарю.

        Args:
            data: Данные для проверки.

        Returns:
            Валидны ли данные.
        """
        return bool(data) and isinstance(data, dict)

    @staticmethod
    def valid_client(client: Optional["ClientType"]) -> TypeGuard["Client"]:
        """Проверка что клиент передан и является синхронным.

        Args:
            client: Клиент для проверки.

        Returns:
            Синхронный ли клиент.
        """
        from zvuk_music import Client

        return isinstance(client, Client)

    @staticmethod
    def valid_async_client(client: Optional["ClientType"]) -> TypeGuard["ClientAsync"]:
        """Проверка что клиент передан и является асинхронным.

        Args:
            client: Клиент для проверки.

        Returns:
            Асинхронный ли клиент.
        """
        from zvuk_music import ClientAsync

        return isinstance(client, ClientAsync)

    @staticmethod
    def is_array_model_data(data: JSONType) -> TypeGuard[List[Dict[str, JSONType]]]:
        """Проверка на соответствие данных массиву словарей.

        Args:
            data: Данные для проверки.

        Returns:
            Валидны ли данные.
        """
        return bool(data) and isinstance(data, list) and all(isinstance(item, dict) for item in data)

    @classmethod
    def cleanup_data(cls, data: JSONType, client: Optional["ClientType"]) -> ModelFieldMap:
        """Удаляет незадекларированные поля для текущей модели из сырых данных.

        Note:
            Фильтрует только словарь поле:значение. Иначе вернёт пустой dict.

        Args:
            data: Поля и значения десериализуемого объекта.
            client: Клиент Zvuk Music.

        Returns:
            Отфильтрованные данные.
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
        """Десериализация объекта.

        Note:
            Переопределяется в дочерних классах когда есть вложенные объекты.

        Args:
            data: Поля и значения десериализуемого объекта.
            client: Клиент Zvuk Music.

        Returns:
            Десериализованный объект.
        """
        if not cls.is_dict_model_data(data):
            return None

        return cls(client=client, **cls.cleanup_data(data, client))

    @classmethod
    def de_list(cls, data: JSONType, client: "ClientType") -> Sequence[Self]:
        """Десериализация списка объектов.

        Note:
            Переопределяется в дочерних классах, если необходимо.

        Args:
            data: Список словарей с полями и значениями десериализуемого объекта.
            client: Клиент Zvuk Music.

        Returns:
            Список десериализованных объектов.
        """
        if not cls.is_array_model_data(data):
            return []

        items = [cls.de_json(item, client) for item in data]
        return [item for item in items if item is not None]

    def to_json(self, for_request: bool = False) -> str:
        """Сериализация объекта в JSON строку.

        Args:
            for_request: Подготовить ли объект для отправки в теле запроса.

        Returns:
            Сериализованный в JSON объект.
        """
        return json.dumps(self.to_dict(for_request), ensure_ascii=not _ujson)

    def to_dict(self, for_request: bool = False) -> JSONType:
        """Рекурсивная сериализация объекта в словарь.

        Args:
            for_request: Перевести ли обратно все поля в camelCase.

        Note:
            Исключает из сериализации `client` и `_id_attrs`.

        Returns:
            Сериализованный в dict объект.
        """

        def parse(val: Union["ZvukMusicModel", JSONType]) -> Any:
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
        """Получение ключевых атрибутов объекта.

        Returns:
            Ключевые атрибуты объекта для сравнения.
        """
        return cast(Tuple[str, ...], getattr(self, "_id_attrs", ()))

    def __eq__(self, other: Any) -> bool:
        """Проверка на равенство двух объектов.

        Note:
            Проверка осуществляется по атрибутам, перечисленным в `_id_attrs`.

        Returns:
            Одинаковые ли объекты (по содержимому).
        """
        if isinstance(other, self.__class__):
            return self._get_id_attrs() == other._get_id_attrs()
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Реализация хеш-функции на основе ключевых атрибутов.

        Returns:
            Хеш объекта.
        """
        id_attrs = self._get_id_attrs()
        if not id_attrs:
            return super().__hash__()

        frozen_attrs = tuple(frozenset(attr) if isinstance(attr, list) else attr for attr in id_attrs)
        return hash((self.__class__, frozen_attrs))
