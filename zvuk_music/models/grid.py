"""Grid content models.

Note (RU): Модели сетки контента.
"""

from typing import TYPE_CHECKING, Optional

from zvuk_music.base import ZvukMusicModel
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class GridContentItem(ZvukMusicModel):
    """Grid content item from the Tiny API.

    Attributes:
        id: Item ID.
        type: Item type (e.g., "playlist").

    Note (RU): Элемент сетки контента из Tiny API.
        id: ID элемента.
        type: Тип элемента (например, "playlist").
    """

    client: Optional["ClientType"] = None
    id: str = ""
    type: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.id, self.type)
