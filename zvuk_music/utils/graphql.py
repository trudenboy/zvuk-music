"""GraphQL query loader."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict

GRAPHQL_DIR = Path(__file__).parent.parent / "graphql"


@lru_cache(maxsize=100)
def load_query(name: str) -> str:
    """Загрузка GraphQL запроса из файла.

    Args:
        name: Имя запроса (без расширения .graphql).

    Returns:
        Содержимое GraphQL файла.

    Raises:
        FileNotFoundError: Если файл не найден.
    """
    # Ищем в queries
    query_path = GRAPHQL_DIR / "queries" / f"{name}.graphql"
    if query_path.exists():
        return query_path.read_text(encoding="utf-8")

    # Ищем в mutations
    mutation_path = GRAPHQL_DIR / "mutations" / f"{name}.graphql"
    if mutation_path.exists():
        return mutation_path.read_text(encoding="utf-8")

    raise FileNotFoundError(f"GraphQL file not found: {name}.graphql")


def get_all_queries() -> Dict[str, str]:
    """Получение всех доступных GraphQL запросов.

    Returns:
        Словарь {имя: содержимое} для всех запросов.
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
