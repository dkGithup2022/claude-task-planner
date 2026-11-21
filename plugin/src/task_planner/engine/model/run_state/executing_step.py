"""engine 이 지금 실행 중인 단계. 명령이 단계를 실행하는 동안만 state.json 에 남는다."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutingStep:
    """engine 이 지금 실행 중인 단계. 명령이 단계를 실행하는 동안만 state.json 에 남는다."""

    node_uuid: str
    item_key: str | None
    pid: int  # 단계를 실행 중인 명령의 프로세스 번호
    started_at: str

    def is_alive(self) -> bool:
        """그 프로세스가 아직 있는지. 없으면 끝나지 않고 사라진 실행이다."""
        # shortcut: 번호만 본다. 재부팅 뒤 다른 프로세스가 같은 번호를 받으면 살아 있다고 본다 (드묾).
        # 실제로 생기면 프로세스 시작 시각을 함께 비교한다.
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:  # 있지만 다른 사용자의 프로세스
            return True
        return True
