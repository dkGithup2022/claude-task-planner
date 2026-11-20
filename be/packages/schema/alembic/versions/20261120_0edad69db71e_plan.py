"""plan

Revision ID: 0edad69db71e
Revises:
Create Date: 2026-11-20 17:17:45.327413

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0edad69db71e"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PLAN_STATUSES = ("drafting", "reviewing", "approved", "rejected", "running", "done")


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("request", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(*PLAN_STATUSES, name="planstatus", native_enum=False, length=255),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # 계획의 참여 페르소나. DB FK 제약은 두지 않는다 (autogenerate 가 만든 FK 를 지웠다)
    op.create_table(
        "plan_personas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), nullable=False),
        sa.Column("persona_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plan_personas_plan_id"), "plan_personas", ["plan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_plan_personas_plan_id"), table_name="plan_personas")
    op.drop_table("plan_personas")
    op.drop_table("plans")
