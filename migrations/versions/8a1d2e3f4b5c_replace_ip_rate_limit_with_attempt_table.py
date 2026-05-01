"""Replace IP rate limit storage with attempts table

Revision ID: 8a1d2e3f4b5c
Revises: 4f2d9a8b7c1e
Create Date: 2026-05-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a1d2e3f4b5c"
down_revision: Union[str, None] = "4f2d9a8b7c1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("ip_rate_limits")
    op.create_table(
        "ip_rate_limit_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ip", sa.String(), nullable=False),
        sa.Column("ts", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ip_rate_limit_attempts_ip"),
        "ip_rate_limit_attempts",
        ["ip"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ip_rate_limit_attempts_ip"), table_name="ip_rate_limit_attempts")
    op.drop_table("ip_rate_limit_attempts")
    op.create_table(
        "ip_rate_limits",
        sa.Column("ip", sa.String(), nullable=False),
        sa.Column("attempts", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("ip"),
    )
