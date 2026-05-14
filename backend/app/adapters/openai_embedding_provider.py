from openai import AsyncOpenAI

from app.core.config import settings
from app.ports.embedding_provider import EmbeddingProvider

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """OpenAI 클라이언트를 지연 생성한다."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI Embeddings API를 사용하는 임베딩 포트 어댑터."""

    async def embed_text(self, text: str) -> list[float]:
        response = await get_client().embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIM,
        )
        return response.data[0].embedding
