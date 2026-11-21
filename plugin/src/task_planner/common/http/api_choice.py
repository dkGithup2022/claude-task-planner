"""mock 과 서버 가운데 무엇을 쓸지, 서버 주소는 어디인지. 환경 변수로 정한다 (사용자, 2026-11-19)."""

from __future__ import annotations

import os

API_ENV = "TASK_PLANNER_API"  # mock | server. 없으면 mock
API_URL_ENV = "TASK_PLANNER_API_URL"  # 서버 주소. server 일 때 필요


def uses_server() -> bool:
    """TASK_PLANNER_API 가 server 면 True. 그 밖의 값이나 없으면 mock."""
    return os.environ.get(API_ENV, "mock").strip().lower() == "server"


def api_url(path: str) -> str:
    """서버 주소 + path. 주소가 없으면 ValueError."""
    base = os.environ.get(API_URL_ENV, "").rstrip("/")
    if not base:
        raise ValueError(f"{API_ENV}=server 인데 {API_URL_ENV} 가 없습니다")
    return base + path
