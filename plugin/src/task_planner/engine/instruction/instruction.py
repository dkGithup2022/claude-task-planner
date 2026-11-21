"""메인 세션에 내린 지시. state.json 의 waiting_instruction 으로 저장."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.engine.instruction.instruction_type import InstructionType
from task_planner.engine.request.conversation_request import ConversationRequest
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.engine.request.show_request import ShowRequest
from task_planner.engine.request.subagent_request import SubagentRequest
from task_planner.engine.request.task_request import TaskRequest

# 지시의 내용은 작업이 만든 요청 그대로 (설계 결정). 다시 읽을 때 지시 종류로 요청 타입을 고른다.
_PAYLOAD_TYPE: dict[InstructionType, type[ShowRequest | QuestionRequest | ConversationRequest | SubagentRequest]] = {
    InstructionType.SHOW: ShowRequest,
    InstructionType.ASK: QuestionRequest,
    InstructionType.TALK: ConversationRequest,
    InstructionType.SPAWN: SubagentRequest,
    InstructionType.FINISHED: ShowRequest,  # 보일 글
    InstructionType.FAILED: ShowRequest,  # 보일 글
    InstructionType.WAIT: ShowRequest,  # 보일 글
}


@dataclass(frozen=True, slots=True)
class Instruction:
    """메인 세션에 내린 지시. state.json 의 waiting_instruction 으로 저장."""

    type: InstructionType
    node_uuid: str  # FINISHED 는 루트 노드, FAILED 는 실패한 노드 (시작 전 실패는 ""), WAIT 는 실행 중인 노드
    item_key: str | None
    payload: TaskRequest

    @classmethod
    def finished(cls, root_uuid: str, text: str = "끝났습니다.", skill: str | None = None) -> Instruction:
        return cls(InstructionType.FINISHED, root_uuid, None, ShowRequest(text, skill))

    @classmethod
    def failed(cls, text: str, node_uuid: str = "", item_key: str | None = None) -> Instruction:
        return cls(InstructionType.FAILED, node_uuid, item_key, ShowRequest(text))

    @classmethod
    def wait(cls, text: str, node_uuid: str, item_key: str | None) -> Instruction:
        return cls(InstructionType.WAIT, node_uuid, item_key, ShowRequest(text))
