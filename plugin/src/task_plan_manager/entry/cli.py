"""task_plan_manager 명령. 인자 해석, 실행기 조립, JSON 출력만."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from task_plan_manager.common.clock import utc_now
from task_plan_manager.engine.hook.session_start_hook import on_session_start
from task_plan_manager.engine.hook.stop_hook import on_stop
from task_plan_manager.engine.instruction.instruction_converter import InstructionConverter
from task_plan_manager.engine.model.session.claude_session import ClaudeSession
from task_plan_manager.engine.performer.default_performers import default_performers
from task_plan_manager.engine.port.history.default_history_writer import DefaultHistoryWriter
from task_plan_manager.engine.port.result.default_result_reader import DefaultResultReader
from task_plan_manager.engine.port.result.default_result_writer import DefaultResultWriter
from task_plan_manager.engine.port.run_state.default_run_state_reader import DefaultRunStateReader
from task_plan_manager.engine.port.run_state.default_run_state_writer import DefaultRunStateWriter
from task_plan_manager.engine.port.run_state.run_state_file_converter import RunStateFileConverter
from task_plan_manager.engine.port.session.default_session_reader import DefaultSessionReader
from task_plan_manager.engine.port.session.default_session_writer import DefaultSessionWriter
from task_plan_manager.engine.runner.child_run.default_strategies import default_strategies
from task_plan_manager.engine.runner.flow.default_flow_runner import DefaultFlowRunner
from task_plan_manager.engine.runner.flow.dict_flow_registry import DictFlowRegistry
from task_plan_manager.engine.runner.unit.default_unit_runner import DefaultUnitRunner
from task_plan_manager.workflow.plan_edit.edit_plan import edit_plan, show_plan
from task_plan_manager.workflow.registry import FLOWS
from task_plan_manager.workflow.statusline.draw_statusline import draw_statusline


def build_runner() -> DefaultFlowRunner:
    sessions, runs = DefaultSessionReader(), DefaultRunStateReader()
    performers = default_performers(sessions)
    unit = DefaultUnitRunner(DefaultRunStateWriter(), DefaultHistoryWriter(), DefaultResultReader(),
                             DefaultResultWriter(), performers, default_strategies())  # fmt: skip
    return DefaultFlowRunner(DictFlowRegistry(FLOWS), sessions, DefaultSessionWriter(), runs, DefaultRunStateWriter(),
                             unit, performers, DefaultHistoryWriter())  # fmt: skip


def hook(event: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Claude Code 훅. 세션을 열 때 대화 기록 경로를 적고, 멈추려 할 때 할 일이 남았으면 막는다."""
    if data.get("cwd"):
        os.chdir(data["cwd"])
    sid = str(data.get("session_id") or "")
    if not sid:
        return None
    if event == "session-start":
        on_session_start(sid, data.get("transcript_path"), DefaultSessionReader(), DefaultSessionWriter())
        return None
    return on_stop(sid, data, DefaultSessionReader(), DefaultRunStateReader())


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="task_plan_manager")
    p.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID", "no-session"))
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("flow")
    sub.add_parser("next")
    d = sub.add_parser("done")
    d.add_argument("--answer")
    sub.add_parser("status")
    sub.add_parser("cancel")
    h = sub.add_parser("hook")
    h.add_argument("event", choices=["session-start", "stop"])
    plan = sub.add_parser("plan")  # 흐름 밖에서 계획을 읽고 고친다 (plan-edit 스킬이 부름)
    plan.add_argument("action", choices=["show", "edit"])
    plan.add_argument("plan_id", type=int)
    plan.add_argument("--ops", help='edit 의 {"ops": [...]} JSON. 없으면 표준 입력에서 읽는다')
    sub.add_parser("statusline")  # Claude Code 상태 줄. 표준 입력의 세션 정보로 진행 기록을 그린다
    a = p.parse_args(argv)

    if a.cmd == "hook":
        out = hook(a.event, json.loads(sys.stdin.read() or "{}"))
        if out:
            print(json.dumps(out, ensure_ascii=False))
        return 0
    if a.cmd == "statusline":
        lines = draw_statusline(sys.stdin.read())
        if lines:
            print("\n".join(lines))
        return 0
    if a.cmd == "plan":
        return _print(_plan_command(a.action, a.plan_id, a.ops))
    runner, instructions = build_runner(), InstructionConverter()
    session = _session(a.session)
    if a.cmd == "start":
        return _print(instructions.to_json(runner.start(session, a.flow)))
    if a.cmd == "next":
        return _print(instructions.to_json(runner.next_instruction(session)))
    if a.cmd == "done":
        return _print(instructions.to_json(runner.submit_reply(session, a.answer)))
    if a.cmd == "status":
        state = runner.read_state(session)
        return _print(RunStateFileConverter().to_file(state) if state else {"status": "none"})
    return _print(instructions.to_json(runner.cancel(session)))


def _plan_command(action: str, plan_id: int, ops_text: str | None) -> dict[str, Any]:
    """plan show 는 계획 JSON, plan edit 는 --ops (없으면 표준 입력)의 {"ops": [...]} 를 적용한 결과."""
    if action == "show":
        return show_plan(plan_id)
    try:
        data = json.loads(ops_text if ops_text is not None else (sys.stdin.read() or "{}"))
    except json.JSONDecodeError as error:
        return {"ok": False, "reason": f"표준 입력이 JSON 이 아닙니다: {error}"}
    return edit_plan(plan_id, data)


def _session(session_id: str) -> ClaudeSession:
    """세션 파일이 없으면(훅이 돌지 않음) 대화 기록 경로 없이 만든다."""
    found = DefaultSessionReader().load_session(session_id)
    if found is not None:
        return found
    t = utc_now()
    session = ClaudeSession(session_id, None, None, t, t)
    DefaultSessionWriter().save_session(session)
    return session


def _print(obj: dict[str, Any]) -> int:
    print(json.dumps(obj, ensure_ascii=False))
    return 0
