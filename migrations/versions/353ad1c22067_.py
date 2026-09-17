"""empty message

Revision ID: 353ad1c22067
Revises: f0d57567258b
Create Date: 2026-09-15 13:49:10.378074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '353ad1c22067'
down_revision: Union[str, Sequence[str], None] = 'f0d57567258b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('has_private_chat', sa.Boolean(), nullable=False, server_default=sa.false()))

    op.alter_column('users', 'has_private_chat',server_default=None,)

def downgrade() -> None:
    op.drop_column('users', 'has_private_chat')
