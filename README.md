# Mosaic
A basic, flexible game save module for Python.

## Features
* Load and save structured data  (`SaveFile` subclasses) atomically;
* Supports optional Base64 obfuscation (note: not encryption);
* Handles save versioning and migrations;
* Automatically backs up corrupted save files;
* Customizable file extension.

## Installation
Simply include the `mosaic/` folder in your project alongside your `SaveFile` implementations.

## Usage Example
```python
from dataclasses import dataclass
from mosaic import SaveFile, SaveManager

# -----------------------------
# Example SaveFile
# -----------------------------
@dataclass
class GameSave(SaveFile):
    SCHEMA_VERSION = 2  # current save schema version
    version: int
    gold: int
    health: int

    @classmethod
    def default(cls):
        """Return a new default save file."""
        return cls(version=cls.SCHEMA_VERSION, gold=0, health=100)

    @classmethod
    def from_json(cls, data):
        """Load from JSON-like dict."""
        return cls(**data)

    def to_json(self):
        """Serialize to JSON-like dict."""
        return {
            "version": self.version,
            "gold": self.gold,
            "health": self.health,
        }

# -----------------------------
# Example SaveManager
# -----------------------------
class GameSaveManager(SaveManager[GameSave]):
    def migrate_save(self, data, from_version):
        """
        Incrementally migrate old save data to the latest schema version.
        Each version step should be handled in a case block.
        This allows sequential migrations if multiple versions were skipped.
        """
        while from_version < self._save_cls.SCHEMA_VERSION:
            match from_version:
                case 1:
                    # Example migration: version 1 -> 2
                    # Introduce 'health' field with default value 100
                    data["health"] = 100
                    from_version = 2
                case _:
                    raise RuntimeError(f"No migration path from version {from_version}.")

        # Ensure the save data always reflects the latest version
        data["version"] = self._save_cls.SCHEMA_VERSION

# -----------------------------
# Example Usage
# -----------------------------
manager = GameSaveManager(GameSave)

# Load existing save, or create default if missing
save = manager.load("player")

# Update save data
save.gold += 50

# Save updated data
manager.save("player", save)
```

## Notes
* Obfuscation: Base64 encoding is applied automatically if enabled. This does not secure your data, it only makes it less readable;
* Corrupted saves: Mosaic automatically backs up corrupted files and replaces them with defaults to prevent data loss;
* Version migrations: When SCHEMA_VERSION changes, implement logic in migrate_save to adapt old saves.
