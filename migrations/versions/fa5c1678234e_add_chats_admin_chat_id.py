"""add_chats_admin_chat_id

Revision ID: fa5c1678234e
Revises: 4b120997b02a
Create Date: 2026-10-19 14:19:26.787573

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa5c1678234e'
down_revision: Union[str, Sequence[str], None] = '4b120997b02a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column("admin_chat_id", sa.BigInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("chats", "admin_chat_id")
