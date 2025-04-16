import os
from pathlib import Path
from typing import Dict, Tuple, Optional
from collections import OrderedDict


class FileCache:
    """Класс для кэширования дескрипторов открытых файлов с LRU стратегией."""

    def __init__(self, max_size: int):
        self.cache: OrderedDict[Path, Tuple] = OrderedDict()
        self.max_size = max_size

    def get_file(self, file_path: Path) -> Optional[Tuple]:
        """Получить файл из кэша или открыть его, если он отсутствует."""
        if not file_path.is_file():
            return None

        if file_path in self.cache:
            self.cache.move_to_end(file_path)
            return self.cache[file_path]

        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        try:
            fd = open(file_path, 'rb')
            file_size = os.path.getsize(file_path)
            last_modified = os.path.getmtime(file_path)
            self.cache[file_path] = (fd, file_size, last_modified)
            return self.cache[file_path]
        except Exception as e:
            print(f"Error opening file: {e}")
            return None

    def close_all(self):
        """Закрыть все открытые файлы в кэше."""
        for fd, _, _ in self.cache.values():
            fd.close()
        self.cache.clear()