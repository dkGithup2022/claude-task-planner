"""plan edit 의 표준 입력 JSON({"ops": [...]}) → 묶음 동작 목록. 모양이 틀리면 PlanEditRefusedError."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.workflow.plan_edit.op.edit_op import EditOp
from task_plan_manager.workflow.plan_edit.op.insert_op import InsertOp
from task_plan_manager.workflow.plan_edit.op.link_op import LinkOp
from task_plan_manager.workflow.plan_edit.op.merge_op import MergeOp
from task_plan_manager.workflow.plan_edit.op.new_part import NewPart
from task_plan_manager.workflow.plan_edit.op.remove_op import RemoveOp
from task_plan_manager.workflow.plan_edit.op.split_op import SplitOp
from task_plan_manager.workflow.plan_edit.op.split_order import SplitOrder
from task_plan_manager.workflow.plan_edit.op.unlink_op import UnlinkOp
from task_plan_manager.workflow.plan_edit.op.update_op import UpdateOp
from task_plan_manager.workflow.plan_edit.plan_edit_refused_error import PlanEditRefusedError


def read_ops(data: Any) -> tuple[EditOp, ...]:
    """{"ops": [...]} 에서 동작을 차례대로 읽는다. 비어 있으면 거절한다."""
    if not isinstance(data, dict) or not isinstance(data.get("ops"), list) or not data["ops"]:
        raise PlanEditRefusedError('입력은 {"ops": [...]} 이고 동작이 하나 이상 있어야 합니다')
    return tuple(_read_op(index, raw) for index, raw in enumerate(data["ops"], 1))


def _read_op(index: int, raw: Any) -> EditOp:
    """동작 하나. 이름이 없거나 값이 모자라면 몇 번째 동작인지 담아 거절한다."""
    try:
        return _OP_READERS[raw["op"]](raw)
    except (KeyError, TypeError, ValueError) as error:
        raise PlanEditRefusedError(f"{index} 번째 동작을 읽지 못했습니다: {error!r} ({raw})") from error


def _part(raw: dict[str, Any]) -> NewPart:
    return NewPart(str(raw["title"]), str(raw["scope"]), raw.get("output"), raw.get("note"))


def _split(raw: dict[str, Any]) -> SplitOp:
    parts = tuple(_part(item) for item in raw["into"])
    if len(parts) < 2:
        raise ValueError("split 의 into 는 둘 이상이어야 합니다")
    return SplitOp(int(raw["node_id"]), SplitOrder(raw.get("order", "serial")), parts)


def _merge(raw: dict[str, Any]) -> MergeOp:
    node_ids = tuple(dict.fromkeys(int(node_id) for node_id in raw["node_ids"]))  # 겹친 id 는 한 번만
    if len(node_ids) < 2:
        raise ValueError("merge 의 node_ids 는 둘 이상이어야 합니다")
    return MergeOp(node_ids, _part(raw))


def _insert(raw: dict[str, Any]) -> InsertOp:
    after, before = raw.get("after"), raw.get("before")
    return InsertOp(
        None if after is None else int(after),
        None if before is None else int(before),
        NodeKind(raw["kind"]),
        _part(raw),
    )


def _update(raw: dict[str, Any]) -> UpdateOp:
    kind, persona_ids = raw.get("kind"), raw.get("persona_ids")
    return UpdateOp(
        int(raw["node_id"]), raw.get("title"), raw.get("scope"), None if kind is None else NodeKind(kind),
        None if persona_ids is None else tuple(int(persona_id) for persona_id in persona_ids),
        raw.get("output"), raw.get("add_note"),
    )  # fmt: skip


def _remove(raw: dict[str, Any]) -> RemoveOp:
    return RemoveOp(int(raw["node_id"]))


def _link(raw: dict[str, Any]) -> LinkOp:
    return LinkOp(int(raw["from"]), int(raw["to"]))


def _unlink(raw: dict[str, Any]) -> UnlinkOp:
    return UnlinkOp(int(raw["from"]), int(raw["to"]))


_OP_READERS: dict[str, Callable[[dict[str, Any]], EditOp]] = {
    "split": _split, "merge": _merge, "insert": _insert, "remove": _remove, "update": _update,
    "link": _link, "unlink": _unlink,
}  # fmt: skip
