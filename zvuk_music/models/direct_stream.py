"""Direct stream model.

Note (RU): Модель прямого стрима.
"""

from typing import TYPE_CHECKING, Optional

from zvuk_music.base import ZvukMusicModel
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class DirectStream(ZvukMusicModel):
    """Direct (non-DRM) stream URL.

    Attributes:
        stream: Direct stream URL.
        quality: Requested quality.

    Note (RU): Прямой URL стрима (без DRM).
        stream: Прямой URL стрима.
        quality: Запрошенное качество.
    """

    client: Optional["ClientType"] = None
    stream: str = ""
    quality: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.stream,)
