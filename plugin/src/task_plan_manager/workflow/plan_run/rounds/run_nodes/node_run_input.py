"""노드 실행의 입력 글: 작업 지시 본문, 앞 노드 결과의 위치, 결과를 쓸 곳.
앞 노드 결과는 본문을 넣지 않고 위치만 넘긴다. 노드가 Read 로 필요한 만큼 읽는다 (사용자, 2026-11-20).
넘기는 것은 실행 데이터 (확정) 3 절의 조회 결과: 제목, 상태, 회차, result.md, files 목록, 건너뛴 이유."""

from __future__ import annotations

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.dto.result_target import ResultTarget


def node_run_input(plan: Plan, node: PlanNode, prompt_text: str, target: ResultTarget) -> str:
    parts = [
        "# 작업 지시",
        prompt_text.strip(),
        "# 앞 노드의 결과",
        previous_results(plan, node.node_id),
        "# 결과를 쓸 곳",
        f"- 본문: {target.result_path}\n- 여러 파일이면: {target.files_dir}",
    ]
    return "\n\n".join(parts) + "\n"


def previous_results(plan: Plan, node_id: int) -> str:
    """선행 노드마다 상태와 결과 위치 (마지막 회차). 확인 노드의 대화 목표에도 쓴다."""
    folder = DefaultPlanFolderReader()
    lines: list[str] = []
    for pre_id in plan.prerequisites(node_id):
        pre = plan.node(pre_id)
        if pre.status is PlanNodeStatus.SKIPPED:
            run = folder.read_run(plan.plan_id, pre_id)
            reason = run.skipped_reason if run and run.skipped_reason else "이유 없음"
            lines.append(f'- 노드 {pre_id} "{pre.title}": 건너뜀. 이유: {reason}')
            continue
        output = folder.read_output(plan.plan_id, pre_id)
        if output is None:
            lines.append(f'- 노드 {pre_id} "{pre.title}": 결과 없음')
            continue
        lines.append(f'- 노드 {pre_id} "{pre.title}": 완료, {output.round} 회차')
        lines.append(f"  - 결과: {output.result_path}")
        if output.files:
            lines.append("  - 결과 파일: " + ", ".join(str(path) for path in output.files))
    return "\n".join(lines) or "(없음. 계획의 첫 노드)"
