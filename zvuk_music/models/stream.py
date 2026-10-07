"""Streaming models.

Note (RU): Модели стриминга.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Tuple

from zvuk_music.base import ZvukMusicModel
from zvuk_music.enums import Quality
from zvuk_music.exceptions import QualityNotAvailableError, SubscriptionRequiredError
from zvuk_music.utils import model

if TYPE_CHECKING:
    from zvuk_music.base import ClientType


@model
class StreamUrls(ZvukMusicModel):
    """Streaming URLs.

    Attributes:
        mid: 128kbps MP3 URL (always available).
        high: 320kbps MP3 URL (requires subscription).
        flac: FLAC URL without DRM (requires subscription).
        flacdrm: FLAC URL with DRM (requires subscription).

    Note (RU): URL для стриминга.
        mid: URL 128kbps MP3 (всегда доступен).
        high: URL 320kbps MP3 (требует подписку).
        flac: URL FLAC без DRM (требует подписку).
        flacdrm: URL FLAC с DRM (требует подписку).
    """

    client: Optional["ClientType"] = None
    mid: str = ""
    high: Optional[str] = None
    flac: Optional[str] = None
    flacdrm: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.mid,)

    def get_url(self, quality: Quality = Quality.HIGH) -> str:
        """Get URL for the specified quality.

        Args:
            quality: Audio quality.

        Returns:
            URL for downloading/streaming.

        Raises:
            QualityNotAvailableError: If the quality is not available.
            SubscriptionRequiredError: If a subscription is required.

        Note (RU): Получить URL для указанного качества.
        """
        if quality == Quality.FLAC:
            flac_url = self.flac or self.flacdrm
            if not flac_url:
                raise SubscriptionRequiredError("FLAC quality requires subscription")
            return flac_url

        if quality == Quality.HIGH:
            if not self.high:
                raise SubscriptionRequiredError("High quality (320kbps) requires subscription")
            return self.high

        if quality == Quality.MID:
            if not self.mid:
                raise QualityNotAvailableError("Mid quality URL not available")
            return self.mid

        raise QualityNotAvailableError(f"Unknown quality: {quality}")

    def get_best_available(self) -> Tuple[Quality, str]:
        """Get the best available quality.

        Returns:
            Tuple of (quality, URL).

        Note (RU): Получить лучшее доступное качество.
        """
        flac_url = self.flac or self.flacdrm
        if flac_url:
            return (Quality.FLAC, flac_url)
        if self.high:
            return (Quality.HIGH, self.high)
        return (Quality.MID, self.mid)


@model
class Stream(ZvukMusicModel):
    """Stream information with expiration time.

    Attributes:
        expire: Expiration time (ISO 8601).
        expire_delta: Seconds until expiration.
        mid: 128kbps MP3 URL.
        high: 320kbps MP3 URL.
        flac: FLAC URL without DRM.
        flacdrm: FLAC URL with DRM.

    Note (RU): Информация о стриме с временем истечения.
        expire: Время истечения (ISO 8601).
        expire_delta: Секунды до истечения.
        mid: URL 128kbps MP3.
        high: URL 320kbps MP3.
        flac: URL FLAC без DRM.
        flacdrm: URL FLAC с DRM.
    """

    client: Optional["ClientType"] = None
    expire: str = ""
    expire_delta: int = 0
    mid: str = ""
    high: Optional[str] = None
    flac: Optional[str] = None
    flacdrm: Optional[str] = None

    def __post_init__(self) -> None:
        self._id_attrs = (self.mid, self.expire)

    def is_expired(self) -> bool:
        """Check if the URL has expired.

        Note (RU): Проверка, истёк ли срок действия URL.
        """
        if not self.expire:
            return True

        try:
            # Try ISO 8601
            expire_time = datetime.fromisoformat(self.expire.replace("Z", "+00:00"))
            return datetime.now(expire_time.tzinfo) > expire_time
        except (ValueError, TypeError):
            return True

    def get_url(self, quality: Quality = Quality.HIGH) -> str:
        """Get URL for the specified quality.

        Args:
            quality: Audio quality.

        Returns:
            URL for downloading/streaming.

        Raises:
            QualityNotAvailableError: If the quality is not available.
            SubscriptionRequiredError: If a subscription is required.

        Note (RU): Получить URL для указанного качества.
        """
        urls = StreamUrls(
            client=self.client,
            mid=self.mid,
            high=self.high,
            flac=self.flac,
            flacdrm=self.flacdrm,
        )
        return urls.get_url(quality)

    def get_best_available(self) -> Tuple[Quality, str]:
        """Get the best available quality.

        Returns:
            Tuple of (quality, URL).

        Note (RU): Получить лучшее доступное качество.
        """
        urls = StreamUrls(
            client=self.client,
            mid=self.mid,
            high=self.high,
            flac=self.flac,
            flacdrm=self.flacdrm,
        )
        return urls.get_best_available()
