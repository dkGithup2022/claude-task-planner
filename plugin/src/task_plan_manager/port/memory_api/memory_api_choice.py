"""지식 구현 고르기. TASK_PLAN_MANAGER_API=server 면 서버 구현, 아니면 mock."""

from __future__ import annotations

from task_plan_manager.common.http.api_choice import uses_server
from task_plan_manager.port.memory_api.default_memory_api_reader import DefaultMemoryApiReader
from task_plan_manager.port.memory_api.default_memory_api_writer import DefaultMemoryApiWriter
from task_plan_manager.port.memory_api.memory_api_reader import MemoryApiReader
from task_plan_manager.port.memory_api.memory_api_writer import MemoryApiWriter
from task_plan_manager.port.memory_api.mock_memory_api_reader import MockMemoryApiReader
from task_plan_manager.port.memory_api.mock_memory_api_writer import MockMemoryApiWriter


def memory_api_reader() -> MemoryApiReader:
    return DefaultMemoryApiReader() if uses_server() else MockMemoryApiReader()


def memory_api_writer() -> MemoryApiWriter:
    return DefaultMemoryApiWriter() if uses_server() else MockMemoryApiWriter()
