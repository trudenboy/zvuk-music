"""Тесты моделей аудиокниг."""

from zvuk_music.models.book import BookAuthor, SimpleBook


class TestBookAuthor:
    """Тесты BookAuthor."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "5001",
            "rname": "Толстой Лев",
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
        }
        author = BookAuthor.de_json(data, mock_client)

        assert author is not None
        assert author.id == "5001"
        assert author.rname == "Толстой Лев"
        assert author.image is not None

    def test_de_json_none(self, mock_client):
        assert BookAuthor.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert BookAuthor.de_json({}, mock_client) is None

    def test_de_list(self, mock_client):
        data = [
            {"id": "1", "rname": "Author 1"},
            {"id": "2", "rname": "Author 2"},
        ]
        authors = BookAuthor.de_list(data, mock_client)
        assert len(authors) == 2


class TestSimpleBook:
    """Тесты SimpleBook."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "6001",
            "title": "Война и мир",
            "author_names": ["Лев Толстой"],
            "book_authors": [{"id": "5001", "rname": "Толстой Лев", "image": None}],
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
        }
        book = SimpleBook.de_json(data, mock_client)

        assert book is not None
        assert book.id == "6001"
        assert book.title == "Война и мир"
        assert len(book.author_names) == 1
        assert len(book.book_authors) == 1
        assert book.book_authors[0].rname == "Толстой Лев"

    def test_de_json_none(self, mock_client):
        assert SimpleBook.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert SimpleBook.de_json({}, mock_client) is None

    def test_default_empty_lists(self, mock_client):
        book = SimpleBook.de_json({"id": "1", "title": "Test"}, mock_client)
        assert book.author_names == []
        assert book.book_authors == []

    def test_get_authors_str_from_book_authors(self, mock_client):
        """get_authors_str использует book_authors если есть."""
        data = {
            "id": "1",
            "title": "Test",
            "author_names": ["Name Str"],
            "book_authors": [{"id": "1", "rname": "Author RName", "image": None}],
        }
        book = SimpleBook.de_json(data, mock_client)
        assert book.get_authors_str() == "Author RName"

    def test_get_authors_str_fallback(self, mock_client):
        """get_authors_str использует author_names как fallback."""
        data = {
            "id": "1",
            "title": "Test",
            "author_names": ["Лев Толстой"],
        }
        book = SimpleBook.de_json(data, mock_client)
        assert book.get_authors_str() == "Лев Толстой"
