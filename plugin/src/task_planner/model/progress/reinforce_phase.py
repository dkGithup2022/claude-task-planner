"""지식 강화에서 후보 하나가 지나는 과정. 상태 줄의 셋째 줄 글과 누구 차례인지가 여기서 정해진다."""

from __future__ import annotations

from enum import StrEnum


class ReinforcePhase(StrEnum):
    EXTRACT = "extract"  # 대화에서 지식 후보를 뽑는 중 (아직 후보가 없음)
    CHOOSE = "choose"  # 후보를 어떻게 저장할지 사용자가 고를 차례
    DRAFT = "draft"  # 본문 초안을 쓰는 중
    REVIEW = "review"  # 사용자가 본문을 확인하고 저장할지 답할 차례
    FINALIZE = "finalize"  # 대화를 반영해 본문을 최종 정리하는 중
