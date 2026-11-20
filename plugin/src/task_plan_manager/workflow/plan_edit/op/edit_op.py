"""묶음 동작 하나. plan edit 명령이 받는 ops 의 원소."""

from __future__ import annotations

from task_plan_manager.workflow.plan_edit.op.insert_op import InsertOp
from task_plan_manager.workflow.plan_edit.op.link_op import LinkOp
from task_plan_manager.workflow.plan_edit.op.merge_op import MergeOp
from task_plan_manager.workflow.plan_edit.op.remove_op import RemoveOp
from task_plan_manager.workflow.plan_edit.op.split_op import SplitOp
from task_plan_manager.workflow.plan_edit.op.unlink_op import UnlinkOp
from task_plan_manager.workflow.plan_edit.op.update_op import UpdateOp

EditOp = SplitOp | MergeOp | InsertOp | RemoveOp | UpdateOp | LinkOp | UnlinkOp
