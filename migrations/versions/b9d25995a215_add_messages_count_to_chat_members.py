"""add messages_count to chat_members

Revision ID: b9d25995a215
Revises: ea1dec79f33e
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b9d25995a215"
down_revision: Union[str, None] = "ea1dec79f33e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_members",
        sa.Column("messages_count", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("chat_members", "messages_count")