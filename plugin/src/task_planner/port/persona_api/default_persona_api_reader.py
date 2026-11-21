"""페르소나 목록의 서버 구현. GET {서버 주소}/personas."""

from __future__ import annotations

from task_planner.common.http.api_choice import api_url
from task_planner.common.http.http_json import request_json
from task_planner.common.http.http_json_error import HttpJsonError
from task_planner.model.persona.persona import Persona
from task_planner.port.persona_api.persona_api_converter import PersonaApiConverter
from task_planner.port.persona_api.persona_api_error import PersonaApiError
from task_planner.port.persona_api.persona_api_reader import PersonaApiReader


class DefaultPersonaApiReader(PersonaApiReader):
    def list_personas(self) -> tuple[Persona, ...]:
        # 서버의 페르소나 목록을 받아 Persona 로 바꾼다. 서버 실패는 PersonaApiError 로 바꿔 던진다
        try:
            body = request_json("GET", api_url("/personas"))
        except HttpJsonError as failed:
            raise PersonaApiError(str(failed)) from failed
        return PersonaApiConverter().to_personas(body)
