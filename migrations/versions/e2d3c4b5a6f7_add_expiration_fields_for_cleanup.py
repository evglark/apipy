"""Add expiration fields for cleanup

Revision ID: b1c2d3e4f5a6
Revises: 8a1d2e3f4b5c
Create Date: 2026-05-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2d3c4b5a6f7"
down_revision: Union[str, None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("created_at", sa.BigInteger(), nullable=True))
    op.add_column("refresh_tokens", sa.Column("expires_at", sa.BigInteger(), nullable=True))
    op.add_column("login_attempts", sa.Column("created_at", sa.BigInteger(), nullable=True))
    op.add_column("login_attempts", sa.Column("expires_at", sa.BigInteger(), nullable=True))
    op.add_column(
        "ip_rate_limit_attempts", sa.Column("created_at", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "ip_rate_limit_attempts", sa.Column("expires_at", sa.BigInteger(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("ip_rate_limit_attempts", "expires_at")
    op.drop_column("ip_rate_limit_attempts", "created_at")
    op.drop_column("login_attempts", "expires_at")
    op.drop_column("login_attempts", "created_at")
    op.drop_column("refresh_tokens", "expires_at")
    op.drop_column("refresh_tokens", "created_at")
