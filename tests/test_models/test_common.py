"""Тесты общих моделей (Image, Genre, Label)."""

from zvuk_music.models.common import Animation, Background, Genre, Image, Label


class TestImage:
    """Тесты Image."""

    def test_de_json_valid(self, mock_client):
        data = {"src": "https://cdn-image.zvuk.com/pic?id=123&size={size}&type=artist"}
        image = Image.de_json(data, mock_client)

        assert image is not None
        assert "zvuk.com" in image.src

    def test_de_json_none(self, mock_client):
        assert Image.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert Image.de_json({}, mock_client) is None

    def test_get_url_with_size_param(self, mock_client):
        """get_url подставляет размер в URL с параметром size."""
        image = Image.de_json(
            {"src": "https://cdn-image.zvuk.com/pic?id=123&size=100x100&type=artist"},
            mock_client,
        )
        url = image.get_url(300, 400)
        assert "300x400" in url

    def test_get_url_relative_path(self, mock_client):
        """Относительные пути конвертируются в абсолютные."""
        image = Image.de_json({"src": "/static/img/default.png"}, mock_client)
        url = image.get_url()
        assert url.startswith("https://zvuk.com/static/img/default.png")

    def test_get_url_no_size_param(self, mock_client):
        """URL без параметра size возвращается как есть."""
        image = Image.de_json(
            {"src": "https://cdn-image.zvuk.com/pic?id=123&type=artist"},
            mock_client,
        )
        url = image.get_url(300, 300)
        assert url == "https://cdn-image.zvuk.com/pic?id=123&type=artist"


class TestGenre:
    """Тесты Genre."""

    def test_de_json_valid(self, mock_client):
        data = {"id": "23", "name": "Rock", "short_name": "rock"}
        genre = Genre.de_json(data, mock_client)

        assert genre is not None
        assert genre.id == "23"
        assert genre.name == "Rock"
        assert genre.short_name == "rock"

    def test_de_json_none(self, mock_client):
        assert Genre.de_json(None, mock_client) is None

    def test_de_list(self, mock_client):
        data = [
            {"id": "1", "name": "Rock"},
            {"id": "2", "name": "Pop"},
        ]
        genres = Genre.de_list(data, mock_client)
        assert len(genres) == 2
        assert genres[0].name == "Rock"


class TestLabel:
    """Тесты Label."""

    def test_de_json_valid(self, mock_client):
        data = {"id": "114338", "title": "EMI"}
        label = Label.de_json(data, mock_client)

        assert label is not None
        assert label.id == "114338"
        assert label.title == "EMI"

    def test_de_json_none(self, mock_client):
        assert Label.de_json(None, mock_client) is None


class TestBackground:
    """Тесты Background."""

    def test_de_json_valid(self, mock_client):
        data = {"type": "image", "image": "https://example.com/bg.jpg"}
        bg = Background.de_json(data, mock_client)
        assert bg is not None

    def test_de_json_none(self, mock_client):
        assert Background.de_json(None, mock_client) is None


class TestAnimation:
    """Тесты Animation."""

    def test_de_json_valid(self, mock_client):
        data = {
            "artist_id": "754367",
            "effect": "glow",
            "image": "https://example.com/anim.png",
            "background": {"type": "image", "image": "https://example.com/bg.jpg"},
        }
        anim = Animation.de_json(data, mock_client)

        assert anim is not None
        assert anim.artist_id == "754367"
        assert anim.background is not None

    def test_de_json_none(self, mock_client):
        assert Animation.de_json(None, mock_client) is None
