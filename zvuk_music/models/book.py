"""Audiobook models.

Note (RU): Модели аудиокниг.
"""

from dataclasses import field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.common import Image
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class BookAuthor(ZvukMusicModel):
    """Book author.

    Attributes:
        id: Author ID.
        rname: Reversed name (Last name First name).
        image: Image.

    Note (RU): Автор книги.
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
    """Brief book information.

    Attributes:
        id: Book ID.
        title: Title.
        author_names: Author names.
        book_authors: Book authors.
        image: Cover image.

    Note (RU): Краткая информация о книге.
        id: ID книги.
        title: Название.
        author_names: Имена авторов.
        book_authors: Авторы книги.
        image: Обложка.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    title: str = ""
    author_names: List[str] = field(default_factory=list)
    book_authors: List[BookAuthor] = field(default_factory=list)
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
        if "book_authors" in data_dict:
            data_dict["book_authors"] = BookAuthor.de_list(data_dict["book_authors"], client)

        return cls(client=client, **cls.cleanup_data(data_dict, client))

    def get_authors_str(self) -> str:
        """Get a string with author names.

        Returns:
            Author names separated by commas.

        Note (RU): Получить строку с именами авторов.
        """
        if self.book_authors:
            return ", ".join(a.rname for a in self.book_authors)
        return ", ".join(self.author_names)
