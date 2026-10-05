"""media file_id to string

Revision ID: e5a2b8c4d1f7
Revises: 7c1e2d9a4b3f
"""

from alembic import op
import sqlalchemy as sa

revision = "e5a2b8c4d1f7"
down_revision = "7c1e2d9a4b3f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.alter_column(
        "media",
        "file_id",
        type_=sa.String(255),
        postgresql_using="file_id::varchar"
    )

def downgrade() -> None:
    op.execute("DELETE FROM media")
    op.alter_column(
        "media",
        "file_id",
        type_=sa.Integer(),
        postgresql_using="file_id::integer"
    )