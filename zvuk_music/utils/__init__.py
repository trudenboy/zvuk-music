"""Утилиты библиотеки Zvuk Music API."""

from dataclasses import dataclass
from typing import TypeVar

from typing_extensions import dataclass_transform

T = TypeVar("T")


@dataclass_transform(eq_default=False)
def model(cls: type[T]) -> type[T]:
    """Декоратор для моделей данных.

    Обёртка над @dataclass с отключённым сравнением и repr
    для корректной работы с вложенными объектами.

    Args:
        cls: Класс для декорирования.

    Returns:
        Декорированный класс.
    """
    return dataclass(eq=False, repr=False)(cls)


__all__ = ["model"]
