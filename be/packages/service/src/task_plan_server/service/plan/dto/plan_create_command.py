from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlanCreateCommand:
    """계획 만들기. 이 서비스에는 로그인 사용자가 없어 request_user_id 를 두지 않는다."""

    title: str
    request: str  # 명령서 md
    persona_ids: tuple[int, ...]
