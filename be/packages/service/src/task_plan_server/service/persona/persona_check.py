from collections.abc import Iterable

from task_plan_server.exception.persona.unknown_persona_exception import UnknownPersonaException
from task_plan_server.infrastructure.persona.persona_repository import PersonaRepository


def require_personas(repository: PersonaRepository, persona_ids: Iterable[int] | None) -> None:
    """persona_ids 가 모두 지우지 않은 페르소나인지 본다. 아니면 UnknownPersonaException(400).

    None(고치기에서 보내지 않음)이나 빈 목록이면 볼 것이 없다.
    지식·계획·노드의 만들기·고치기 Usecase 가 Writer 를 부르기 전에 쓴다 (사용자, 2026-11-20).
    """
    if not persona_ids:
        return
    missing = repository.find_missing_ids(list(persona_ids))
    if missing:
        raise UnknownPersonaException(missing)
