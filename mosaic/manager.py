from abc import ABC, abstractmethod
import base64
import json
import os
import time
from typing import Any, Type, TypeVar, Generic

from .save import SaveFile

T = TypeVar("T", bound=SaveFile)

class SaveManager(Generic[T], ABC):
    def __init__(self, save_cls: Type[T], extension: str = ".mosaic") -> None:
        self._save_cls = save_cls
        self._extension = (extension if extension.startswith(".") else f".{extension}")
    
    def load(self, path: str) -> T:
        """Loads a save file, handling versioning and corruption."""
        
        path = self._with_extension(path)

        # Save doesn't exist yet
        if not os.path.exists(path):
            return self._save_cls.default()

        try:
            with open(path, "rb") as f:
                encoded = f.read()

            decoded = base64.b64decode(encoded)
            data = json.loads(decoded.decode("utf-8"))

            self._handle_version(data)

            return self._save_cls.from_json(data)

        except Exception:
            backup_path = self._backup_corrupted_save(path)
            print(f"[Mosaic] Error loading save at {path}. Renamed to {backup_path}.")
            return self._save_cls.default()

    def save(self, path: str, save: T) -> None:
        """Saves data atomically."""
        
        path = self._with_extension(path)

        data = save.to_json()
        data['version'] = self._save_cls.SCHEMA_VERSION
        temp_path = path + ".tmp"

        try:
            json_bytes = json.dumps(data, indent=4).encode("utf-8")
            encoded = base64.b64encode(json_bytes)

            with open(temp_path, "wb") as f:
                f.write(encoded)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, path)

        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def _handle_version(self, data: dict[str, Any]) -> None:
        save_version = data['version']

        if save_version > self._save_cls.SCHEMA_VERSION:
            raise RuntimeError(f"Save version {save_version} is newer than {self._save_cls.SCHEMA_VERSION}.")

        if save_version < self._save_cls.SCHEMA_VERSION:
            self.migrate_save(data, save_version)

    @abstractmethod
    def migrate_save(self, data: dict[str, Any], from_version: int) -> None:
        """Subclasses must implement migration logic. Should mutate `data` in-place and update version."""
        raise NotImplementedError

    def _backup_corrupted_save(self, path: str) -> str:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{os.path.splitext(path)[0]}_{timestamp}{self._extension}.bak"

        os.rename(path, backup_path)
        return backup_path

    def _with_extension(self, path: str) -> str:
        if not path.endswith(self._extension):
            return path + self._extension
        return path
