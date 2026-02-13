from dataclasses import dataclass
from typing import ClassVar, Type, TypeVar

T = TypeVar('T', bound='SaveFile')

@dataclass
class SaveFile:
    SCHEMA_VERSION: ClassVar[int] = 1

    # your fields here, e.g.:
    # gold: int
    # health: int
    
    @classmethod
    def default(cls: Type[T]) -> T:
        """Returns a fresh default save instance."""
        
        return cls(
            version=cls.SCHEMA_VERSION,
            #gold=0,
            #health=100,
        )

    @classmethod
    def from_json(cls: Type[T], data: dict) -> T:
        return cls(
            version=data['version'],
            #gold=data['gold'],
            #health=data['health'],
        )

    def to_json(self) -> dict:
        return {
            'version': self.version,
            #'gold': self.gold,
            #'health': self.health,
        }
