"""add hunger_updated_at and eat_human cooldown

Revision ID: a7c3e9f1b2d4
Revises: 7c1e2d9a4b3f
"""
from alembic import op
import sqlalchemy as sa

revision = "a7c3e9f1b2d4"
down_revision = "7c1e2d9a4b3f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ghouls",
        sa.Column("hunger", sa.Integer(), server_default="100", nullable=False),
    )

    op.add_column(
        "ghouls",
        sa.Column(
            "hunger_updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    op.execute("ALTER TABLE ghouls ADD COLUMN IF NOT EXISTS hunger INTEGER NOT NULL DEFAULT 100")
    op.execute("ALTER TABLE ghouls ADD COLUMN IF NOT EXISTS hunger_updated_at TIMESTAMPTZ NOT NULL DEFAULT now()")
    op.execute("ALTER TYPE cooldown_action ADD VALUE IF NOT EXISTS 'EAT_HUMAN'")


def downgrade() -> None:
    op.drop_column("ghouls", "hunger_updated_at")
    op.drop_column("ghouls", "hunger")