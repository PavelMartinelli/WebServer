import pytest
from pathlib import Path

from src.server.ServerConfig import ServerConfig


@pytest.fixture
def sample_config():
    return ServerConfig()

@pytest.fixture
def static_dir(tmp_path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "test.txt").write_text("test content")
    return static

@pytest.fixture
def server_config(static_dir):
    config = ServerConfig()
    config.static_dir = str(static_dir)
    config.open_file_cache_max_size = 2
    return config