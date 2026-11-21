"""InstructionConverter: 지시 ↔ JSON. 메인 세션에 출력하고 state.json 의 waiting_instruction 으로 저장한다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.instruction.instruction import _PAYLOAD_TYPE, Instruction
from task_planner.engine.instruction.instruction_type import InstructionType
from task_planner.engine.request.conversation_request import ConversationRequest
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.engine.request.show_request import ShowRequest
from task_planner.engine.request.subagent_request import SubagentRequest
from task_planner.engine.request.task_request import TaskRequest


class InstructionConverter:
    def to_json(self, ins: Instruction) -> dict[str, Any]:
        expected = _PAYLOAD_TYPE.get(ins.type)
        if expected is None or not isinstance(ins.payload, expected):
            raise TypeError(f"{ins.type} 지시에 넣을 수 없는 요청: {type(ins.payload).__name__}")
        return {"type": ins.type.value, "node_uuid": ins.node_uuid, "item_key": ins.item_key,
                "payload": self._payload_to_json(ins.payload)}  # fmt: skip

    def to_data(self, d: dict[str, Any]) -> Instruction:
        """지시 종류로 요청 타입을 고른다."""
        kind = InstructionType(d["type"])
        return Instruction(kind, d["node_uuid"], d.get("item_key"), self._payload_to_data(kind, d["payload"]))

    def _payload_to_json(self, p: TaskRequest) -> dict[str, Any]:
        if isinstance(p, ShowRequest):  # skill 은 있을 때만 싣는다
            return {"text": p.text, "skill": p.skill} if p.skill else {"text": p.text}
        if isinstance(p, QuestionRequest):
            return {"question": p.question, "choices": list(p.choices)}
        if isinstance(p, ConversationRequest):
            return {"goal": p.goal, "opening": p.opening}
        if isinstance(p, SubagentRequest):
            return {"agent": p.agent, "message": p.message}
        raise TypeError(f"지시로 내보낼 수 없는 요청: {type(p).__name__}")

    def _payload_to_data(self, kind: InstructionType, d: dict[str, Any]) -> TaskRequest:
        expected = _PAYLOAD_TYPE[kind]
        if expected is ShowRequest:
            return ShowRequest(d["text"], d.get("skill"))
        if expected is QuestionRequest:
            return QuestionRequest(d["question"], tuple(d["choices"]))
        if expected is ConversationRequest:
            return ConversationRequest(d["goal"], d["opening"])
        return SubagentRequest(d["agent"], d["message"])
