import json
import os


class ServerConfig:
    """Класс для загрузки и хранения конфигурации сервера."""
    def __init__(self, config_path: str = "server.conf"):
        self.config_path = config_path
        self.host = "127.0.0.1"
        self.port = 8080
        self.static_dir = "../../static"
        self.open_file_cache_enabled = True
        self.open_file_cache_max_size = 100
        self.load_config()

    def load_config(self):
        """Загрузить конфигурацию из файла."""
        if not os.path.exists(self.config_path):
            print(f"Конфигурационный файл {self.config_path} не найден. Используются настройки по умолчанию.")
            return

        with open(self.config_path, "r") as config_file:
            config = json.load(config_file)
            self.host = config.get("host", self.host)
            self.port = config.get("port", self.port)
            self.static_dir = config.get("static_dir", self.static_dir)
            open_file_cache_config = config.get("open_file_cache", {})
            self.open_file_cache_enabled = open_file_cache_config.get("enabled", self.open_file_cache_enabled)
            self.open_file_cache_max_size = open_file_cache_config.get("max_size", self.open_file_cache_max_size)