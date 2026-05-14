from typing import Protocol


class EmbeddingProvider(Protocol):
    """텍스트를 의미 벡터로 변환하는 외부 기능 포트."""

    async def embed_text(self, text: str) -> list[float]:
        """입력 텍스트의 임베딩 벡터를 반환한다."""
        ...
