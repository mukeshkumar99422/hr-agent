# repeated LLM calls on the same input return instantly from disk

import os
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".langchain_cache.db"
)


def setup_cache():
    """Initialize SQLite LLM cache. Call once at app startup."""
    set_llm_cache(SQLiteCache(database_path=CACHE_PATH))
    print(f"✓ LLM cache enabled → {CACHE_PATH}")


if __name__ == "__main__":
    setup_cache()