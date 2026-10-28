"""add birthday to users

Revision ID: cc0fd3cf5fbd
Revises: fa5c1678234e
Create Date: 2026-10-28 11:53:38.069761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc0fd3cf5fbd'
down_revision: Union[str, Sequence[str], None] = 'fa5c1678234e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("birthday_day", sa.SmallInteger(), nullable=True))
    op.add_column("users", sa.Column("birthday_month", sa.SmallInteger(), nullable=True))
    op.add_column("users", sa.Column("birthday_year", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "birthday_year")
    op.drop_column("users", "birthday_month")
    op.drop_column("users", "birthday_day")