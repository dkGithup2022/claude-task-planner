"""DefaultSessionWriter: 세션 파일을 쓴다."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.engine.model.session.claude_session import ClaudeSession
from task_plan_manager.engine.port.run_location import session_dir
from task_plan_manager.engine.port.session.session_file_converter import SessionFileConverter
from task_plan_manager.engine.port.session.session_writer import SessionWriter


class DefaultSessionWriter(SessionWriter):
    def save_session(self, session: ClaudeSession) -> None:
        files.write_json(session_dir(session.session_id) / "session.json", SessionFileConverter().to_file(session))
