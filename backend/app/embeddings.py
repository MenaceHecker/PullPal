import hashlib
import math
from typing import Protocol

from app.config import get_settings

EMBEDDING_DIM = 1536


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


class FakeEmbeddingProvider:
    """Deterministic, dependency-free embedding used whenever no real
    provider is configured, so the demo works for a reviewer with no API
    key set up. It's a hashed bag-of-words projection: words that show up
    in both pieces of text end up pulling their vectors closer together,
    which is good enough for runbook search to find the right section. It's
    not a real model and won't capture actual meaning, just word overlap."""

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * EMBEDDING_DIM
        words = text.lower().split()
        if not words:
            return vector

        for word in words:
            digest = hashlib.sha256(word.encode()).digest()
            for i in range(0, len(digest) - 1, 2):
                dim = int.from_bytes(digest[i : i + 2], "big") % EMBEDDING_DIM
                sign = 1.0 if digest[i] % 2 == 0 else -1.0
                vector[dim] += sign

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class OpenAIEmbeddingProvider:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self._model, input=text)
        return response.data[0].embedding


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIEmbeddingProvider(settings.openai_api_key, settings.embedding_model)
    return FakeEmbeddingProvider()
