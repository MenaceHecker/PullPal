import math

from app.embeddings import EMBEDDING_DIM, FakeEmbeddingProvider


def test_embed_returns_the_expected_dimension() -> None:
    provider = FakeEmbeddingProvider()
    vector = provider.embed("hello world")
    assert len(vector) == EMBEDDING_DIM


def test_embed_is_deterministic() -> None:
    provider = FakeEmbeddingProvider()
    assert provider.embed("checkout error") == provider.embed("checkout error")


def test_embed_is_normalized() -> None:
    provider = FakeEmbeddingProvider()
    vector = provider.embed("some reasonably long piece of text to embed")
    norm = math.sqrt(sum(v * v for v in vector))
    assert math.isclose(norm, 1.0, abs_tol=1e-6)


def test_empty_text_returns_zero_vector() -> None:
    provider = FakeEmbeddingProvider()
    assert provider.embed("") == [0.0] * EMBEDDING_DIM


def test_shared_words_pull_vectors_closer_than_unrelated_text() -> None:
    provider = FakeEmbeddingProvider()

    def cosine_similarity(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b, strict=True))

    base = provider.embed("checkout service returns 500 errors on shipping_method")
    related = provider.embed("shipping_method missing causes checkout 500 errors")
    unrelated = provider.embed("payments provider connection pool timeout")

    assert cosine_similarity(base, related) > cosine_similarity(base, unrelated)
