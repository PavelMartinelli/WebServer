import json
import os
from src.server.ServerConfig import ServerConfig


def test_default_config(tmp_path):
    config = ServerConfig(config_path=str(tmp_path / "nonexistent.json"))
    assert config.host == "127.0.0.1"
    assert config.port == 8080


def test_config_loading(tmp_path):
    config_file = tmp_path / "server.json"
    config_data = {
        "host": "0.0.0.0",
        "port": 8000,
        "open_file_cache": {"enabled": False, "max_size": 50}
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    config = ServerConfig(config_path=str(config_file))
    assert config.host == "0.0.0.0"
    assert config.port == 8000
    assert not config.open_file_cache_enabled
    assert config.open_file_cache_max_size == 50