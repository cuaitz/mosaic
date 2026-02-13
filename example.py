from dataclasses import dataclass
from typing import ClassVar, Any

from mosaic import SaveFile, SaveManager

# Concrete Save File
@dataclass
class GameSave(SaveFile):
    SCHEMA_VERSION: ClassVar[int] = 2

    version: int
    gold: int
    health: int

    @classmethod
    def default(cls) -> "GameSave":
        return cls(
            version=cls.SCHEMA_VERSION,
            gold=0,
            health=100,
        )

    @classmethod
    def from_json(cls, data: dict) -> "GameSave":
        return cls(
            version=data["version"],
            gold=data["gold"],
            health=data["health"],
        )

    def to_json(self) -> dict:
        return {
            "version": self.version,
            "gold": self.gold,
            "health": self.health,
        }


# Concrete Save Manager
class GameSaveManager(SaveManager[GameSave]):
    def migrate_save(self, data: dict[str, Any], from_version: int) -> None:
        """Example migration:
        1 -> 2: introduce 'health' field (default 100)
        """
        
        while from_version < self._save_cls.SCHEMA_VERSION:
            match from_version:
                case 1:
                    data["health"] = 100
                    data["version"] = 2
                    from_version = 2
                case _:
                    raise RuntimeError(f"No migration path from version {from_version}.")

# Example Usage
def main():
    manager = GameSaveManager(GameSave)

    # Load save (creates default if missing or corrupted)
    
    save_name: str = "player"
    
    save: GameSave = manager.load(save_name)

    print("Loaded save:")
    print(f"Version: {save.version}")
    print(f"Gold: {save.gold}")
    print(f"Health: {save.health}")

    # Modify save data
    save.gold += 50
    save.health -= 10

    # Save it back
    manager.save("player", save)

    print("\nSave updated and written to disk.")

if __name__ == "__main__":
    main()
