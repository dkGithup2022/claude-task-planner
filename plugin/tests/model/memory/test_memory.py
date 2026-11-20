from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.model.memory.memory_kind import MemoryKind
from task_plan_manager.model.memory.memory_source import MemorySource


def test_should_append_body_with_numbered_mark_and_keep_original():
    original = Memory(2, MemoryKind.KNOWLEDGE, "테이블 설계", "배열은 별도 테이블", (1,), ())
    first = original.append("FK 는 기존을 따른다", (MemorySource("fk 걸지 마", 1),))
    second = first.append("이름은 복수형", ())

    assert second.body == (
        "배열은 별도 테이블\n\n****** KNOWLEDGE APPENDED 1 ********\nFK 는 기존을 따른다"
        "\n\n****** KNOWLEDGE APPENDED 2 ********\n이름은 복수형"
    )
    assert second.sources == (MemorySource("fk 걸지 마", 1),)
    assert original.body == "배열은 별도 테이블"
