"""Общие модели данных."""

from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.enums import BackgroundType
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class Image(ZvukMusicModel):
    """Изображение.

    Attributes:
        src: URL изображения или путь /static/...
        h: Высота.
        w: Ширина.
        palette: Основной цвет палитры.
        palette_bottom: Дополнительный цвет палитры.
    """

    client: Optional["ClientType"] = None
    src: str = ""
    h: Optional[int] = None
    w: Optional[int] = None
    palette: Optional[str] = None
    palette_bottom: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.src,)

    def get_url(self, width: int = 300, height: int = 300) -> str:
        """Получить URL изображения с указанным размером.

        Args:
            width: Ширина изображения.
            height: Высота изображения.

        Returns:
            URL изображения.
        """
        src = self.src

        # Обработка относительных путей
        if src.startswith("/"):
            src = f"https://zvuk.com{src}"

        # Обработка параметра size
        parsed = urlparse(src)
        if "size" in parse_qs(parsed.query):
            query_dict = parse_qs(parsed.query, keep_blank_values=True)
            query_dict["size"] = [f"{width}x{height}"]
            new_query = urlencode(query_dict, doseq=True)
            src = urlunparse(parsed._replace(query=new_query))

        return src


@model
class Label(ZvukMusicModel):
    """Лейбл / мейджор.

    Attributes:
        id: ID лейбла.
        title: Название лейбла.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)


@model
class Genre(ZvukMusicModel):
    """Жанр.

    Attributes:
        id: ID жанра.
        name: Название жанра.
        short_name: Короткое название.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    name: str = ""
    short_name: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)


@model
class Background(ZvukMusicModel):
    """Фон.

    Attributes:
        type: Тип фона.
        image: URL изображения.
        color: Цвет.
        gradient: Градиент.
    """

    client: Optional["ClientType"] = None
    type: Optional[BackgroundType] = None
    image: Optional[str] = None
    color: Optional[Any] = None
    gradient: Optional[Any] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.type, self.image)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        # Конвертация type в enum
        if "type" in data_dict and data_dict["type"]:
            try:
                data_dict["type"] = BackgroundType(data_dict["type"])
            except ValueError:
                pass

        return cls(client=client, **cls.cleanup_data(data_dict, client))


@model
class Animation(ZvukMusicModel):
    """Анимация артиста.

    Attributes:
        artist_id: ID артиста.
        effect: Эффект.
        image: URL изображения.
        background: Фон.
    """

    client: Optional["ClientType"] = None
    artist_id: str = ""
    effect: Optional[str] = None
    image: Optional[str] = None
    background: Optional[Background] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.artist_id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "background" in data_dict:
            data_dict["background"] = Background.de_json(data_dict["background"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))
