"""memory_embedding

지식의 검색용 벡터 열 embedding (vector, 차원 없음) 과 그 벡터를 만든 모델 이름 열 embedding_model.
차원을 정하지 않아 모델을 바꿔도 이 열은 그대로다. 차원이 정해진 열에만 HNSW 인덱스를 걸 수 있어
인덱스는 두지 않는다. 벡터는 벡터 검색을 켠 서버가 저장할 때와 시작할 때 채운다.

Revision ID: bddbb4ecf910
Revises: fc4ad6b1e3bd
Create Date: 2026-11-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "bddbb4ecf910"
down_revision: str | None = "fc4ad6b1e3bd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # vector 확장은 fc4ad6b1e3bd (memory_search_tokens) 에서 켰다
    op.add_column("memories", sa.Column("embedding", Vector(), nullable=True))
    op.add_column("memories", sa.Column("embedding_model", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("memories", "embedding_model")
    op.drop_column("memories", "embedding")
