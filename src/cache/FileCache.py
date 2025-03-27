import os
from pathlib import Path
from typing import Dict, Tuple, Optional


class FileCache:
    """Класс для кэширования дескрипторов открытых файлов."""
    def __init__(self, max_size: int):
        self.cache: Dict[Path, Tuple] = {}
        self.max_size = max_size

    def get_file(self, file_path: Path) -> Optional[Tuple]:
        """Получить файл из кэша или открыть его, если он отсутствует."""
        if file_path in self.cache:
            return self.cache[file_path]
        elif len(self.cache) < self.max_size:
            file_descriptor = open(file_path, 'rb')
            file_size = os.path.getsize(file_path)
            last_modified = os.path.getmtime(file_path)
            self.cache[file_path] = (file_descriptor, file_size, last_modified)
            return self.cache[file_path]
        else:
            return None

    def close_all(self):
        """Закрыть все открытые файлы в кэше."""
        for file_descriptor, _, _ in self.cache.values():
            file_descriptor.close()
        self.cache.clear()