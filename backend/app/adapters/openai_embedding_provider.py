from app.ports.embedding_provider import EmbeddingProvider
from app.services import embedding as embed_svc


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI Embeddings API를 사용하는 임베딩 포트 어댑터."""

    async def embed_text(self, text: str) -> list[float]:
        return await embed_svc.embed_text(text)
