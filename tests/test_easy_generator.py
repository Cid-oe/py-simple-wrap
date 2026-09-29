from collections.abc import Generator
import string

import pytest

from py_simple_package.src.py_simple import (
    generate_random_hex as root_generate_random_hex,
)
from py_simple_package.src.py_simple.easy_generator import (
    EasyGeneratorError,
    generate_random_hex,
)


def test_generate_random_hex_exported_at_root():
    assert root_generate_random_hex is generate_random_hex


def test_generate_random_hex_default_parameters():
    gen = generate_random_hex()
    assert isinstance(gen, Generator)

    results = list(gen)
    assert len(results) == 1
    val = results[0]
    assert len(val) == 16
    assert all(c in string.hexdigits for c in val)


@pytest.mark.parametrize("length", [1, 2, 7, 16, 32, 64])
def test_generate_random_hex_length(length):
    gen = generate_random_hex(length=length, count=1)
    results = list(gen)
    assert len(results) == 1
    assert len(results[0]) == length
    assert all(c in string.hexdigits for c in results[0])


@pytest.mark.parametrize("count", [1, 3, 5])
def test_generate_random_hex_count(count):
    results = list(generate_random_hex(length=8, count=count))
    assert len(results) == count
    assert all(len(item) == 8 for item in results)


def test_generate_random_hex_positional_args():
    results = list(generate_random_hex(12, 2))
    assert len(results) == 2
    assert all(len(item) == 12 for item in results)


def test_generate_random_hex_lazy_iteration():
    gen = generate_random_hex(length=10, count=3)
    first = next(gen)
    assert len(first) == 10
    remaining = list(gen)
    assert len(remaining) == 2


def test_generate_random_hex_uniqueness():
    results = list(generate_random_hex(length=16, count=10))
    assert len(set(results)) == 10


def test_generate_random_hex_mocked(monkeypatch):
    monkeypatch.setattr(
        "py_simple_package.src.py_simple.easy_generator.secrets.token_hex",
        lambda n: "0123456789abcdef",
    )
    results = list(generate_random_hex(length=10, count=2))
    assert results == ["0123456789", "0123456789"]


@pytest.mark.parametrize("length", [0, -1, -10, "16", None, 1.5, False])
def test_generate_random_hex_rejects_invalid_length(length):
    with pytest.raises(EasyGeneratorError, match="at least 1"):
        generate_random_hex(length=length)


@pytest.mark.parametrize("count", [0, -1, -5, "2", None, 2.5, False])
def test_generate_random_hex_rejects_invalid_count(count):
    with pytest.raises(EasyGeneratorError, match="at least 1"):
        generate_random_hex(length=16, count=count)
