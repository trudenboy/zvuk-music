"""Тесты моделей подкастов."""

from zvuk_music.models.podcast import Episode, Podcast, PodcastAuthor, SimpleEpisode, SimplePodcast


class TestPodcastAuthor:
    """Тесты PodcastAuthor."""

    def test_creation(self, mock_client):
        author = PodcastAuthor(client=mock_client, id="1", name="Host")
        assert author.id == "1"
        assert author.name == "Host"


class TestSimplePodcast:
    """Тесты SimplePodcast."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "7001",
            "title": "Tech Podcast",
            "explicit": False,
            "image": {"src": "https://cdn-image.zvuk.com/pic"},
            "authors": [{"id": "1001", "name": "Host"}],
        }
        podcast = SimplePodcast.de_json(data, mock_client)

        assert podcast is not None
        assert podcast.id == "7001"
        assert podcast.title == "Tech Podcast"
        assert len(podcast.authors) == 1
        assert podcast.authors[0].name == "Host"

    def test_de_json_none(self, mock_client):
        assert SimplePodcast.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert SimplePodcast.de_json({}, mock_client) is None

    def test_default_empty_authors(self, mock_client):
        podcast = SimplePodcast.de_json({"id": "1", "title": "Test"}, mock_client)
        assert podcast.authors == []

    def test_de_list(self, mock_client):
        data = [
            {"id": "1", "title": "Podcast 1"},
            {"id": "2", "title": "Podcast 2"},
        ]
        podcasts = SimplePodcast.de_list(data, mock_client)
        assert len(podcasts) == 2


class TestPodcast:
    """Тесты Podcast."""

    def test_de_json_full(self, mock_client, sample_podcast_data):
        podcast = Podcast.de_json(sample_podcast_data, mock_client)

        assert podcast is not None
        assert podcast.id == "7001"
        assert podcast.title == "Tech Podcast"
        assert podcast.description == "A tech podcast"
        assert podcast.availability == 2
        assert podcast.image is not None
        assert len(podcast.authors) == 1
        assert len(podcast.episodes) == 2

    def test_de_json_none(self, mock_client):
        assert Podcast.de_json(None, mock_client) is None

    def test_de_json_empty(self, mock_client):
        assert Podcast.de_json({}, mock_client) is None

    def test_default_empty_lists(self, mock_client):
        podcast = Podcast.de_json({"id": "1", "title": "Test"}, mock_client)
        assert podcast.authors == []
        assert podcast.episodes == []

    def test_is_liked_false(self, mock_client, sample_podcast_data):
        podcast = Podcast.de_json(sample_podcast_data, mock_client)
        assert podcast.is_liked() is False

    def test_is_liked_true(self, mock_client):
        data = {
            "id": "1",
            "title": "Test",
            "collection_item_data": {"id": "ci1", "item_status": "liked"},
        }
        podcast = Podcast.de_json(data, mock_client)
        assert podcast.is_liked() is True


class TestSimpleEpisode:
    """Тесты SimpleEpisode."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "8001",
            "title": "Episode 1",
            "explicit": False,
            "duration": 1800,
            "publication_date": "2024-01-15",
            "image": None,
        }
        episode = SimpleEpisode.de_json(data, mock_client)

        assert episode is not None
        assert episode.id == "8001"
        assert episode.duration == 1800

    def test_de_json_none(self, mock_client):
        assert SimpleEpisode.de_json(None, mock_client) is None


class TestEpisode:
    """Тесты Episode."""

    def test_de_json_valid(self, mock_client):
        data = {
            "id": "8001",
            "title": "Episode 1",
            "explicit": False,
            "description": "First episode",
            "duration": 1800,
            "availability": 2,
            "publication_date": "2024-01-15",
            "image": None,
            "podcast": {
                "id": "7001",
                "title": "Tech Podcast",
                "explicit": False,
                "image": None,
            },
            "collection_item_data": None,
        }
        episode = Episode.de_json(data, mock_client)

        assert episode is not None
        assert episode.id == "8001"
        assert episode.podcast is not None
        assert episode.podcast.id == "7001"

    def test_de_json_none(self, mock_client):
        assert Episode.de_json(None, mock_client) is None

    def test_get_duration_str(self, mock_client):
        episode = Episode.de_json(
            {"id": "1", "title": "Test", "duration": 3661},
            mock_client,
        )
        assert episode.get_duration_str() == "61:01"
