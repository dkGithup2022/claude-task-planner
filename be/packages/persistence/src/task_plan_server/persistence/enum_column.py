from enum import StrEnum

from sqlalchemy import Enum


def value_enum(kind: type[StrEnum]) -> Enum:
    """StrEnum 컬럼. VARCHAR(255) 에 값(소문자)을 저장한다.

    SQLAlchemy 기본은 이름(대문자)을 저장한다. 이 서비스의 enum 값은 CLI 와 같은 소문자이고
    이름과 다르므로 values_callable 로 값을 저장하게 한다. SQL 로 직접 읽을 때도 API 값과 같다.
    """
    return Enum(
        kind,
        native_enum=False,
        length=255,
        values_callable=lambda members: [member.value for member in members],
    )
