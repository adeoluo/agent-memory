from __future__ import annotations

import numpy as np
import pytest

from agent_memory import HashingEmbedder
from agent_memory.embedding import from_blob, to_blob


def test_deterministic_unit_vectors() -> None:
    embedder = HashingEmbedder(dimension=64)
    first = embedder.embed("My favorite editor is Neovim")
    second = HashingEmbedder(dimension=64).embed("My favorite editor is Neovim")
    assert first.shape == (64,)
    assert first.dtype == np.float32
    assert np.allclose(first, second)
    assert float(np.linalg.norm(first)) == pytest.approx(1.0, abs=1e-5)


def test_morphological_variants_are_closer_than_unrelated_text() -> None:
    embedder = HashingEmbedder()
    query = embedder.embed("preferred editor")
    related = embedder.embed("my editor preference")
    unrelated = embedder.embed("weather in Lisbon")
    assert float(query @ related) > float(query @ unrelated)


def test_empty_text_is_zero_vector() -> None:
    vector = HashingEmbedder(dimension=16).embed("the and of")
    assert not vector.any()


def test_blob_round_trip_and_validation() -> None:
    vector = HashingEmbedder(dimension=32).embed("round trip")
    assert np.array_equal(from_blob(to_blob(vector)), vector)
    with pytest.raises(ValueError):
        HashingEmbedder(dimension=4)
