"""Lyrics model.

Note (RU): Модель текста песни.
"""

from typing import TYPE_CHECKING, Optional

from zvuk_music.base import ZvukMusicModel
from zvuk_music.enums import LyricsType
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class Lyrics(ZvukMusicModel):
    """Track lyrics.

    Attributes:
        lyrics: Lyrics text (LRC format or plain text).
        type: Lyrics type (subtitle=LRC, lyrics=plain).
        translation: Optional translation text.

    Note (RU): Текст песни.
        lyrics: Текст (LRC формат или обычный текст).
        type: Тип текста (subtitle=LRC, lyrics=обычный).
        translation: Опциональный перевод.
    """

    client: Optional["ClientType"] = None
    lyrics: str = ""
    type: Optional[str] = None
    translation: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.lyrics,)

    @property
    def lyrics_type(self) -> Optional[LyricsType]:
        """Get the lyrics type as an enum value.

        Note (RU): Получить тип текста как значение перечисления.
        """
        if self.type:
            try:
                return LyricsType(self.type)
            except ValueError:
                return None
        return None

    @property
    def is_synced(self) -> bool:
        """Check if lyrics are synced (LRC format).

        Note (RU): Проверить, синхронизирован ли текст (формат LRC).
        """
        return self.lyrics_type == LyricsType.SUBTITLE
