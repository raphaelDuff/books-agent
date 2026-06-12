from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Configuration for the recommendation agent (OpenAI + Weaviate + guards).

    Follows the same pydantic-settings pattern as ``AuthSettings``; values come
    from the environment / ``.env``.
    """

    openai_api_key: str
    openai_chat_model: str = "gpt-5-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    weaviate_url: str = "http://localhost:8080"
    weaviate_collection: str = "Book"

    # text-to-SQL guard tuning
    sql_max_limit: int = 50
    sql_statement_timeout_ms: int = 5000

    # data-prep only
    books_csv_path: str = "../books.csv"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
