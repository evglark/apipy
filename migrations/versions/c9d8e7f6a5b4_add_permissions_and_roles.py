"""add permissions and roles

Revision ID: c9d8e7f6a5b4
Revises: b1a2c3d4e5f6
Create Date: 2026-05-01 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c9d8e7f6a5b4"
down_revision = "b1a2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.ForeignKeyConstraint(["role"], ["roles.name"]),
        sa.PrimaryKeyConstraint("role", "permission_id"),
    )

    op.execute("INSERT INTO roles(name) SELECT DISTINCT role FROM users")
    op.execute("INSERT INTO roles(name) SELECT 'user' WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name='user')")

    op.create_foreign_key(
        "fk_users_role_roles",
        "users",
        "roles",
        ["role"],
        ["name"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_role_roles", "users", type_="foreignkey")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
