"""진행 기록 쓰기 구현. .plan/<plan_id>/progress.jsonl 에 한 줄씩 덧붙인다."""

from __future__ import annotations

import os

from task_plan_manager.common import files
from task_plan_manager.common.clock import utc_now
from task_plan_manager.model.progress.progress_event import ProgressDetail, ProgressEvent
from task_plan_manager.port.local.plan_folder.plan_folder_location import plan_dir, progress_file
from task_plan_manager.port.local.progress_log.progress_event_file_converter import ProgressEventFileConverter
from task_plan_manager.port.local.progress_log.progress_log_writer import ProgressLogWriter

SESSION_ID_ENV = "CLAUDE_CODE_SESSION_ID"  # Claude Code 가 Bash 로 부른 명령에 넣어 주는 지금 세션 id


class DefaultProgressLogWriter(ProgressLogWriter):
    def append(self, event: ProgressEvent) -> None:
        # 한 줄을 한 번의 쓰기로 덧붙인다. 노드가 동시에 끝나 동시에 써도 줄이 섞이지 않는다
        files.append_jsonl(progress_file(event.plan_id), ProgressEventFileConverter().to_file(event))

    def report(self, plan_id: int, detail: ProgressDetail) -> None:
        # Claude Code 밖에서 불렸으면 상태 줄이 없으므로 남기지 않는다.
        # 이 작업 폴더의 계획이 아니면(계획 폴더가 없음) 남기지 않는다. 빈 계획 폴더가 생기지 않게 하려고.
        # 쓰기 실패는 삼킨다
        session_id = os.environ.get(SESSION_ID_ENV)
        if not session_id or not plan_dir(plan_id).is_dir():
            return
        try:
            self.append(ProgressEvent(at=utc_now(), session_id=session_id, plan_id=plan_id, detail=detail))
        except OSError:
            return
