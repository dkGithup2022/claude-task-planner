from enum import StrEnum


class PlanNodeStatus(StrEnum):
    """노드가 실행에서 어디까지 왔는지. 값은 CLI 와 같은 소문자다.

    서버는 바꾸는 순서를 검사하지 않는다. 사용자가 대화로 상태를 되돌려 고칠 수 있어야 한다.
    """

    TODO = "todo"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"
