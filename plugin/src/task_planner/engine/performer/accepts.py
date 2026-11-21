"""수행자가 받는 요청 종류 표."""

from __future__ import annotations

from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.request.code_request import CodeRequest
from task_planner.engine.request.conversation_request import ConversationRequest
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.engine.request.question_request import QuestionRequest
from task_planner.engine.request.show_request import ShowRequest
from task_planner.engine.request.subagent_request import SubagentRequest
from task_planner.engine.request.task_request import TaskRequest

# 수행자가 받는 요청 종류. create 때 작업의 request_type 과 맞는지 검사한다
ACCEPTS: dict[PerformedBy, type[TaskRequest]] = {
    PerformedBy.CODE: CodeRequest,
    PerformedBy.CLAUDE_P: PromptRequest,
    PerformedBy.MAIN_SESSION_SHOW: ShowRequest,
    PerformedBy.MAIN_SESSION_ASK: QuestionRequest,
    PerformedBy.MAIN_SESSION_TALK: ConversationRequest,
    PerformedBy.SUBAGENT: SubagentRequest,
}
