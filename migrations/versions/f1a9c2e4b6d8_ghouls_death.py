"""ghouls death fields"""

from alembic import op
import sqlalchemy as sa

revision = "f1a9c2e4b6d8"
down_revision = "d4e8a1c0b7f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ghouls",
        sa.Column("deaths", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ghouls",
        sa.Column("is_dead", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "ghouls",
        sa.Column("death_cause", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ghouls", "death_cause")
    op.drop_column("ghouls", "is_dead")
    op.drop_column("ghouls", "deaths")