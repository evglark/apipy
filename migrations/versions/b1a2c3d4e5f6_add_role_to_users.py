"""add role to users

Revision ID: b1a2c3d4e5f6
Revises: 4f2d9a8b7c1e
Create Date: 2026-05-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b1a2c3d4e5f6"
down_revision = "e2d3c4b5a6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(), nullable=False, server_default="user"),
    )


def downgrade() -> None:
    op.drop_column("users", "role")
