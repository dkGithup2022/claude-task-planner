"""memory

Revision ID: 5054c231fd89
Revises: 69138c91383e
Create Date: 2026-11-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5054c231fd89"
down_revision: str | None = "69138c91383e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MEMORY_KINDS = ("knowledge", "attitude", "plan")


def upgrade() -> None:
    op.create_table(
        "memories",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(*MEMORY_KINDS, name="memorykind", native_enum=False, length=255),
            nullable=False,
        ),
        sa.Column("theme", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # 자식 테이블. DB FK 제약은 두지 않는다 (autogenerate 가 만든 FK 를 지웠다)
    op.create_table(
        "memory_personas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("memory_id", sa.BigInteger(), nullable=False),
        sa.Column("persona_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_memory_personas_memory_id"), "memory_personas", ["memory_id"], unique=False
    )
    op.create_table(
        "memory_sources",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("memory_id", sa.BigInteger(), nullable=False),
        sa.Column("quote", sa.Text(), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_memory_sources_memory_id"), "memory_sources", ["memory_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_memory_sources_memory_id"), table_name="memory_sources")
    op.drop_table("memory_sources")
    op.drop_index(op.f("ix_memory_personas_memory_id"), table_name="memory_personas")
    op.drop_table("memory_personas")
    op.drop_table("memories")
