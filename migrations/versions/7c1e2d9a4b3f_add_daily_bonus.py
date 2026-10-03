"""add daily bonus

Revision ID: 7c1e2d9a4b3f
Revises: b9d25995a215
Create Date: 2026-10-02 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '7c1e2d9a4b3f'
down_revision: Union[str, Sequence[str], None] = 'b9d25995a215'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE cooldown_action ADD VALUE IF NOT EXISTS 'DAILY_BONUS'")
    op.add_column(
        'users',
        sa.Column(
            'effects',
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column('users', 'effects')