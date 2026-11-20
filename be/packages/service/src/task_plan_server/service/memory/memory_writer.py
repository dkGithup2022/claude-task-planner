from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory import Memory
from task_plan_server.model.memory.memory_identity import MemoryIdentity

from .dto.memory_create_command import MemoryCreateCommand
from .dto.memory_update_command import MemoryUpdateCommand


class MemoryWriter(ABC):
    @abstractmethod
    def create(self, command: MemoryCreateCommand) -> MemoryIdentity:
        """새 지식. 본문과 근거는 받은 그대로 저장한다."""

    @abstractmethod
    def update(self, command: MemoryUpdateCommand) -> Memory:
        """값이 있는 필드만 받은 그대로 바꾼다. 없으면 MemoryNotFoundException."""

    @abstractmethod
    def delete(self, identity: MemoryIdentity) -> None:
        """지식을 지운다. 없으면 MemoryNotFoundException."""
