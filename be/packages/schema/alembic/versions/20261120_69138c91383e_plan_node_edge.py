"""plan_node_edge

Revision ID: 69138c91383e
Revises: 0edad69db71e
Create Date: 2026-11-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "69138c91383e"
down_revision: str | None = "0edad69db71e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NODE_KINDS = ("document", "research", "code", "hitl")
NODE_STATUSES = ("todo", "running", "done", "failed", "skipped")


def _audit_columns() -> list[sa.Column]:
    return [
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "plan_nodes",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(*NODE_KINDS, name="nodekind", native_enum=False, length=255),
            nullable=False,
        ),
        sa.Column("output_spec", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(*NODE_STATUSES, name="plannodestatus", native_enum=False, length=255),
            nullable=False,
        ),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plan_nodes_plan_id"), "plan_nodes", ["plan_id"], unique=False)
    # 노드의 담당 페르소나. DB FK 제약은 두지 않는다 (autogenerate 가 만든 FK 를 지웠다)
    op.create_table(
        "plan_node_personas",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("node_id", sa.BigInteger(), nullable=False),
        sa.Column("persona_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plan_node_personas_node_id"), "plan_node_personas", ["node_id"], unique=False
    )
    op.create_table(
        "plan_edges",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("plan_id", sa.BigInteger(), nullable=False),
        sa.Column("from_node_id", sa.BigInteger(), nullable=False),
        sa.Column("to_node_id", sa.BigInteger(), nullable=False),
        *_audit_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plan_edges_plan_id"), "plan_edges", ["plan_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_plan_edges_plan_id"), table_name="plan_edges")
    op.drop_table("plan_edges")
    op.drop_index(op.f("ix_plan_node_personas_node_id"), table_name="plan_node_personas")
    op.drop_table("plan_node_personas")
    op.drop_index(op.f("ix_plan_nodes_plan_id"), table_name="plan_nodes")
    op.drop_table("plan_nodes")
