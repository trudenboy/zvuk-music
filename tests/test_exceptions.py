"""Тесты исключений."""

from zvuk_music.exceptions import (
    BadRequestError,
    BotDetectedError,
    GraphQLError,
    NetworkError,
    NotFoundError,
    QualityNotAvailableError,
    SubscriptionRequiredError,
    TimedOutError,
    UnauthorizedError,
    ZvukMusicError,
)


class TestExceptionHierarchy:
    """Все исключения наследуют ZvukMusicError."""

    def test_network_error(self):
        assert issubclass(NetworkError, ZvukMusicError)

    def test_timed_out_error(self):
        assert issubclass(TimedOutError, NetworkError)
        assert issubclass(TimedOutError, ZvukMusicError)

    def test_bad_request_error(self):
        assert issubclass(BadRequestError, ZvukMusicError)

    def test_unauthorized_error(self):
        assert issubclass(UnauthorizedError, ZvukMusicError)

    def test_not_found_error(self):
        assert issubclass(NotFoundError, ZvukMusicError)

    def test_graphql_error(self):
        assert issubclass(GraphQLError, ZvukMusicError)

    def test_subscription_required(self):
        assert issubclass(SubscriptionRequiredError, ZvukMusicError)

    def test_quality_not_available(self):
        assert issubclass(QualityNotAvailableError, ZvukMusicError)

    def test_bot_detected(self):
        assert issubclass(BotDetectedError, ZvukMusicError)


class TestExceptionMessages:
    """Каждое исключение сохраняет message."""

    def test_base_message(self):
        e = ZvukMusicError("test message")
        assert e.message == "test message"
        assert str(e) == "test message"

    def test_network_error_message(self):
        e = NetworkError("connection failed")
        assert e.message == "connection failed"

    def test_timed_out_message(self):
        e = TimedOutError("request timed out")
        assert e.message == "request timed out"


class TestGraphQLError:
    """Тесты GraphQLError."""

    def test_str_with_errors(self):
        """Форматирование GraphQLError с errors list."""
        errors = [
            {"message": "Field 'foo' not found"},
            {"message": "Variable 'id' required"},
        ]
        e = GraphQLError("GraphQL request failed", errors=errors)
        s = str(e)
        assert "GraphQL request failed" in s
        assert "Field 'foo' not found" in s
        assert "Variable 'id' required" in s

    def test_str_without_errors(self):
        """GraphQLError без errors list."""
        e = GraphQLError("GraphQL request failed")
        assert str(e) == "GraphQL request failed"

    def test_errors_default_empty(self):
        """errors по умолчанию — пустой список."""
        e = GraphQLError("test")
        assert e.errors == []

    def test_errors_preserved(self):
        """errors сохраняются."""
        errors = [{"message": "error1"}]
        e = GraphQLError("test", errors=errors)
        assert len(e.errors) == 1
        assert e.errors[0]["message"] == "error1"
