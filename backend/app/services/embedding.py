from openai import AsyncOpenAI

from app.core.config import settings

_client: AsyncOpenAI | None = None

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


def get_client() -> AsyncOpenAI:
    """테스트에서 embed_text를 쉽게 패치할 수 있도록 OpenAI 클라이언트를 지연 생성한다."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed_text(text: str) -> list[float]:
    """
    OpenAI 임베딩 API를 호출한다. 항성 생성/수정에서만 호출하고 GET에서는 절대 호출하지 않는다.

    Args:
        text: 임베딩할 원문 텍스트. 항성에서는 title과 content를 합친 문자열을 넘긴다.
    """
    response = await get_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIM,
    )
    return response.data[0].embedding
