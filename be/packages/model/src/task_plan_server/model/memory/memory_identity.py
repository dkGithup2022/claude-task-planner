from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryIdentity:
    memory_id: int
