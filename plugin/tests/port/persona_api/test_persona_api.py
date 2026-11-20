from task_plan_manager.model.persona.persona import Persona
from task_plan_manager.port.persona_api.default_persona_api_reader import DefaultPersonaApiReader
from task_plan_manager.port.persona_api.mock_persona_api_reader import MockPersonaApiReader
from task_plan_manager.port.persona_api.persona_api_choice import persona_api_reader
from task_plan_manager.port.persona_api.persona_api_error import PersonaApiError


def test_should_make_first_personas_in_mock_when_file_is_missing(mock_data_dir):
    personas = MockPersonaApiReader().list_personas()
    assert personas[0] == Persona(1, "dankim-persona", "사용자의 기본 작업 역할")
    assert len(personas) == 2 and (mock_data_dir / "personas.json").exists()


def test_should_choose_mock_unless_api_env_says_server():
    assert isinstance(persona_api_reader(), MockPersonaApiReader)


def test_should_read_personas_from_server(fake_api):
    fake_api.answer("GET", "/personas", {"personas": [{"persona_id": 7, "name": "fe", "description": "프론트"}]})
    reader = persona_api_reader()
    assert isinstance(reader, DefaultPersonaApiReader)
    assert reader.list_personas() == (Persona(7, "fe", "프론트"),)


def test_should_raise_persona_api_error_when_server_fails(fake_api):
    fake_api.answer("GET", "/personas", {"error": "꺼짐"}, status=500)
    try:
        DefaultPersonaApiReader().list_personas()
        raise AssertionError("PersonaApiError 가 나야 한다")
    except PersonaApiError as failed:
        assert "(500)" in str(failed)
