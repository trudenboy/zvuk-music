"""GraphQL query loader."""

from functools import lru_cache
from pathlib import Path
from typing import Dict

GRAPHQL_DIR = Path(__file__).parent.parent / "graphql"


@lru_cache(maxsize=100)
def load_query(name: str) -> str:
    """Load a GraphQL query from file.

    Args:
        name: Query name (without .graphql extension).

    Returns:
        GraphQL file contents.

    Raises:
        FileNotFoundError: If file is not found.

    Note (RU): Загрузка GraphQL запроса из файла.
    """
    # Search in queries
    query_path = GRAPHQL_DIR / "queries" / f"{name}.graphql"
    if query_path.exists():
        return query_path.read_text(encoding="utf-8")

    # Search in mutations
    mutation_path = GRAPHQL_DIR / "mutations" / f"{name}.graphql"
    if mutation_path.exists():
        return mutation_path.read_text(encoding="utf-8")

    raise FileNotFoundError(f"GraphQL file not found: {name}.graphql")


def get_all_queries() -> Dict[str, str]:
    """Get all available GraphQL queries.

    Returns:
        Dictionary {name: contents} for all queries.

    Note (RU): Получение всех доступных GraphQL запросов.
    """
    queries: Dict[str, str] = {}

    queries_dir = GRAPHQL_DIR / "queries"
    if queries_dir.exists():
        for file in queries_dir.glob("*.graphql"):
            name = file.stem
            queries[name] = file.read_text(encoding="utf-8")

    mutations_dir = GRAPHQL_DIR / "mutations"
    if mutations_dir.exists():
        for file in mutations_dir.glob("*.graphql"):
            name = file.stem
            queries[name] = file.read_text(encoding="utf-8")

    return queries
