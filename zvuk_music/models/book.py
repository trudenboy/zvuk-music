"""Модели аудиокниг."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.common import Image
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class BookAuthor(ZvukMusicModel):
    """Автор книги.

    Attributes:
        id: ID автора.
        rname: Имя в обратном порядке (Фамилия Имя).
        image: Изображение.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    rname: str = ""
    image: Optional[Image] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))


@model
class SimpleBook(ZvukMusicModel):
    """Краткая информация о книге.

    Attributes:
        id: ID книги.
        title: Название.
        author_names: Имена авторов.
        book_authors: Авторы книги.
        image: Обложка.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    author_names: List[str] = None  # type: ignore[assignment]
    book_authors: List[BookAuthor] = None  # type: ignore[assignment]
    image: Optional[Image] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)
        if self.author_names is None:
            self.author_names = []
        if self.book_authors is None:
            self.book_authors = []

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data_dict: Dict[str, Any] = data.copy()

        if "image" in data_dict:
            data_dict["image"] = Image.de_json(data_dict["image"], client)
        if "book_authors" in data_dict:
            data_dict["book_authors"] = BookAuthor.de_list(data_dict["book_authors"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_authors_str(self) -> str:
        """Получить строку с именами авторов.

        Returns:
            Имена авторов через запятую.
        """
        if self.book_authors:
            return ", ".join(a.rname for a in self.book_authors)
        return ", ".join(self.author_names)
