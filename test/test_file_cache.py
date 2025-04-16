import os
from pathlib import Path
from src.cache.FileCache import FileCache


def test_file_cache_lru_eviction(tmp_path):
    cache = FileCache(max_size=2)

    file1 = tmp_path / "file1.txt"
    file1.write_text("content1")
    file2 = tmp_path / "file2.txt"
    file2.write_text("content2")
    file3 = tmp_path / "file3.txt"
    file3.write_text("content3")

    assert cache.get_file(file1) is not None
    assert cache.get_file(file2) is not None

    cache.get_file(file1)

    assert cache.get_file(file3) is not None

    assert file1 in cache.cache
    assert file3 in cache.cache
    assert file2 not in cache.cache


def test_cache_close(tmp_path):
    cache = FileCache(max_size=1)
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    assert cache.get_file(test_file) is not None

    cache.close_all()
    assert len(cache.cache) == 0
    assert test_file.exists()