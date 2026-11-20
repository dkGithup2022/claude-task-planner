from abc import ABC, abstractmethod

from task_plan_server.model.persona.persona import Persona
from task_plan_server.model.persona.persona_identity import PersonaIdentity
from task_plan_server.model.persona.persona_read import PersonaRead


class PersonaRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[PersonaRead]:
        """지우지 않은 페르소나 전부. persona_id 순. 쓰는 지식 수와 계획 수를 담는다."""

    @abstractmethod
    def save(self, persona: Persona) -> Persona:
        """페르소나 저장 (신규·수정). 저장한 페르소나를 id 와 함께 돌려준다."""

    @abstractmethod
    def exists_by_name(self, name: str, exclude: PersonaIdentity | None) -> bool:
        """지우지 않은 페르소나 가운데 이 이름이 있는지. exclude(고칠 때 자기 자신)는 뺀다."""

    @abstractmethod
    def find_write_by_id(self, identity: PersonaIdentity) -> Persona | None:
        """페르소나 Write 모델 조회. 지운 페르소나는 없음으로 본다."""

    @abstractmethod
    def find_by_id(self, identity: PersonaIdentity) -> PersonaRead | None:
        """페르소나 하나와 쓰는 지식 수·계획 수. 지운 페르소나는 없음으로 본다."""

    @abstractmethod
    def delete_by_id(self, identity: PersonaIdentity) -> None:
        """페르소나 soft-delete. 이미 지웠으면 no-op. 쓰는 곳 검사는 부르는 쪽이 한다."""

    @abstractmethod
    def find_missing_ids(self, persona_ids: list[int]) -> list[int]:
        """지우지 않은 페르소나에 없는 id. 받은 순서, 겹치지 않게. 모두 있으면 []."""
