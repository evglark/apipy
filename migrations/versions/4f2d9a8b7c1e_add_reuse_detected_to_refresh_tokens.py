"""Add reuse_detected flag to refresh tokens

Revision ID: 4f2d9a8b7c1e
Revises: d754be8679bc
Create Date: 2026-05-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4f2d9a8b7c1e"
down_revision: Union[str, None] = "d754be8679bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("reuse_detected", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("refresh_tokens", "reuse_detected", server_default=None)


def downgrade() -> None:
    op.drop_column("refresh_tokens", "reuse_detected")
