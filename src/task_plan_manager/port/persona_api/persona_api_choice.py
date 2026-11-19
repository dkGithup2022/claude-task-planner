"""페르소나 목록 구현 고르기. TASK_PLAN_MANAGER_API=server 면 서버 구현, 아니면 mock."""

from __future__ import annotations

from task_plan_manager.common.http.api_choice import uses_server
from task_plan_manager.port.persona_api.default_persona_api_reader import DefaultPersonaApiReader
from task_plan_manager.port.persona_api.mock_persona_api_reader import MockPersonaApiReader
from task_plan_manager.port.persona_api.persona_api_reader import PersonaApiReader


def persona_api_reader() -> PersonaApiReader:
    return DefaultPersonaApiReader() if uses_server() else MockPersonaApiReader()
