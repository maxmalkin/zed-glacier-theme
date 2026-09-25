"""A typed cache with decorators, properties, and string interpolation."""
from dataclasses import dataclass
from typing import Final, Generic, TypeVar

T = TypeVar("T")
MAX_ENTRIES: Final[int] = 128


@dataclass(frozen=True)
class Entry(Generic[T]):
    key: str
    value: T
    enabled: bool = True


class Cache(Generic[T]):
    """Store entries and format a compact summary."""

    def __init__(self, label: str, *, capacity: int = MAX_ENTRIES) -> None:
        self.label = label
        self.capacity = capacity
        self._entries: dict[str, Entry[T]] = {}

    @property
    def count(self) -> int:
        return len(self._entries)

    def insert(self, entry: Entry[T]) -> bool:
        if self.count >= self.capacity or not entry.enabled:
            return False
        self._entries[entry.key] = entry
        return True

    def lookup(self, key: str) -> Entry[T] | None:
        return self._entries.get(key)

    @classmethod
    def empty(cls, label: str) -> "Cache[T]":
        return cls(label=label, capacity=32)

    def summary(self) -> str:
        # Keep comments readable beside bright syntax.
        keys = ", ".join(key for key in self._entries if key.startswith("api"))
        return f"{self.label}: {self.count:03d} entries\n{keys}"
