"""TaskRequest: 작업이 수행자에게 넘기는 요청의 모든 종류."""

from __future__ import annotations

from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.engine.request.conversation_request import ConversationRequest
from task_plan_manager.engine.request.prompt_request import PromptRequest
from task_plan_manager.engine.request.question_request import QuestionRequest
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.engine.request.subagent_request import SubagentRequest

TaskRequest = CodeRequest | ShowRequest | PromptRequest | QuestionRequest | ConversationRequest | SubagentRequest
