"""페르소나 목록의 mock 구현. mock 폴더의 personas.json 을 읽고, 없으면 처음 값으로 만들어 둔다."""

from __future__ import annotations

from task_planner.common import files
from task_planner.common.mock_data import mock_dir
from task_planner.model.persona.persona import Persona
from task_planner.port.persona_api.persona_api_converter import PersonaApiConverter
from task_planner.port.persona_api.persona_api_reader import PersonaApiReader

# 처음 값: 데이터·API 문서의 GET /personas 응답 예시 그대로 (mock 기본 페르소나)
FIRST_PERSONAS = {
    "personas": [
        {"persona_id": 1, "name": "dankim-persona", "description": "사용자의 기본 작업 역할"},
        {"persona_id": 2, "name": "be-developer", "description": "백엔드 개발 역할"},
    ]
}


class MockPersonaApiReader(PersonaApiReader):
    def list_personas(self) -> tuple[Persona, ...]:
        # personas.json 이 없으면 처음 값으로 만든 뒤, 그 파일을 읽어 돌려준다
        personas_path = mock_dir() / "personas.json"
        if not personas_path.exists():
            files.write_json(personas_path, FIRST_PERSONAS)
        return PersonaApiConverter().to_personas(files.read_json(personas_path))
