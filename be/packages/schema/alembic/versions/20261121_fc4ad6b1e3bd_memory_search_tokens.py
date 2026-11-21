"""memory_search_tokens

지식의 검색용 낱말 열 search_tokens (tsvector, 작업 이름 무게 A·본문 무게 B) 와 GIN 인덱스.
벡터 검색(vector) 과 부분 글자 유사도(pg_trgm) 확장도 켠다 (DB 이미지 pgvector/pgvector:pg16).
낱말은 서버(kiwi)가 만들므로 이미 있는 지식은 서버가 시작할 때 채운다.

Revision ID: fc4ad6b1e3bd
Revises: f6618d7f484f
Create Date: 2026-11-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "fc4ad6b1e3bd"
down_revision: str | None = "f6618d7f484f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.add_column(
        "memories",
        sa.Column(
            "search_tokens",
            postgresql.TSVECTOR(),
            server_default=sa.text("''::tsvector"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_memories_search_tokens",
        "memories",
        ["search_tokens"],
        unique=False,
        postgresql_using="gin",
    )


def downgrade() -> None:
    # 확장은 다른 곳에서 쓸 수 있어 지우지 않는다
    op.drop_index("ix_memories_search_tokens", table_name="memories", postgresql_using="gin")
    op.drop_column("memories", "search_tokens")
