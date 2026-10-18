"""add chats.captcha_enabled

Revision ID: 4b120997b02a
Revises: f1a9c2e4b6d8
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4b120997b02a"
down_revision: Union[str, Sequence[str], None] = "f1a9c2e4b6d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column(
            "captcha_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("chats", "captcha_enabled")