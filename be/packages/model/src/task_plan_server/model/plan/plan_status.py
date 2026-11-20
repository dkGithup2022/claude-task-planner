from enum import StrEnum


class PlanStatus(StrEnum):
    """계획이 어느 단계에 있는지. 값은 CLI 와 같은 소문자다.

    서버는 바꾸는 순서를 검사하지 않는다. 흐름을 LLM 이 돌리므로
    사용자가 대화로 상태를 되돌려 고칠 수 있어야 한다 (사용자, 2026-11-20).
    "실패" 는 없다. 실패한 노드가 있어도 계획은 RUNNING 이다.
    """

    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    RUNNING = "running"
    DONE = "done"
