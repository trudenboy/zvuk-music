"""Модели профиля."""

from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from zvuk_music.base import JSONType, ZvukMusicModel
from zvuk_music.models.common import Image
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class SimpleProfile(ZvukMusicModel):
    """Краткая информация о профиле.

    Attributes:
        id: ID профиля.
        name: Имя.
        description: Описание.
        image: Изображение.
    """

    client: Optional["ClientType"] = None
    id: str = ""
    name: str = ""
    description: Optional[str] = None
    image: Optional[Image] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)

        return cls(client=client, **cls.cleanup_data(data, client))


@model
class ExternalProfile(ZvukMusicModel):
    """Внешний профиль (Сбер ID).

    Attributes:
        birthday: День рождения (timestamp).
        email: Email.
        external_id: ID во внешней системе.
        first_name: Имя.
        last_name: Фамилия.
        middle_name: Отчество.
        gender: Пол.
        phone: Телефон.
        type: Тип профиля.
    """

    client: Optional["ClientType"] = None
    birthday: Optional[int] = None
    email: Optional[str] = None
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    type: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.external_id,)


@model
class ProfileResult(ZvukMusicModel):
    """Результат запроса профиля.

    Attributes:
        is_anonymous: Анонимный ли пользователь.
        allow_explicit: Разрешён ли explicit контент.
        birthday: День рождения (timestamp).
        created: Дата создания (timestamp).
        email: Email.
        external_profile: Внешний профиль.
        gender: Пол.
        id: ID пользователя.
        image: Изображение.
        is_active: Активен ли.
        is_agreement: Принято ли соглашение.
        is_editor: Редактор ли.
        is_registered: Зарегистрирован ли.
        name: Имя.
        phone: Телефон.
        registered: Дата регистрации (timestamp).
        token: Токен авторизации.
        username: Имя пользователя.
    """

    client: Optional["ClientType"] = None
    is_anonymous: Optional[bool] = None
    allow_explicit: Optional[bool] = None
    birthday: Optional[int] = None
    created: Optional[int] = None
    email: Optional[str] = None
    external_profile: Optional[ExternalProfile] = None
    gender: Optional[str] = None
    id: Optional[int] = None
    image: Optional[Image] = None
    is_active: Optional[bool] = None
    is_agreement: Optional[bool] = None
    is_editor: Optional[bool] = None
    is_registered: Optional[bool] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    registered: Optional[int] = None
    token: str = ""
    username: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.id, self.token)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "image" in data:
            data["image"] = Image.de_json(data["image"], client)
        if "external_profile" in data:
            data["external_profile"] = ExternalProfile.de_json(data["external_profile"], client)

        return cls(client=client, **cls.cleanup_data(data, client))

    def is_authorized(self) -> bool:
        """Проверка, авторизован ли пользователь (не анонимный)."""
        return not self.is_anonymous


@model
class Profile(ZvukMusicModel):
    """Профиль пользователя.

    Attributes:
        result: Данные профиля.
    """

    client: Optional["ClientType"] = None
    result: Optional[ProfileResult] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.result,)

    @classmethod
    def de_json(cls, data: JSONType, client: "ClientType") -> Optional[Self]:
        if not cls.is_dict_model_data(data):
            return None

        data = data.copy()

        if "result" in data:
            data["result"] = ProfileResult.de_json(data["result"], client)

        return cls(client=client, **cls.cleanup_data(data, client))

    def is_authorized(self) -> bool:
        """Проверка, авторизован ли пользователь."""
        if self.result:
            return self.result.is_authorized()
        return False

    @property
    def token(self) -> str:
        """Токен авторизации."""
        if self.result:
            return self.result.token
        return ""
