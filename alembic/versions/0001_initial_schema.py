"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "some_providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_url", sa.String(length=2048), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_some_providers_id"), "some_providers", ["id"], unique=False)

    op.create_table(
        "some_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_id", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=2048), nullable=False),
        sa.Column("country_code", sa.String(length=10), nullable=False),
        sa.Column("uploads_playlist_id", sa.String(length=255), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["provider_id"], ["some_providers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id"),
    )
    op.create_index(op.f("ix_some_accounts_id"), "some_accounts", ["id"], unique=False)

    op.create_table(
        "some_account_thumbnails",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("social_media_account", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["social_media_account"], ["some_accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_some_account_thumbnails_id"),
        "some_account_thumbnails",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_some_account_thumbnails_social_media_account"),
        "some_account_thumbnails",
        ["social_media_account"],
        unique=False,
    )

    op.create_table(
        "some_account_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("social_media_account", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=False),
        sa.Column("published", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["social_media_account"], ["some_accounts.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id"),
    )
    op.create_index(
        op.f("ix_some_account_items_id"), "some_account_items", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_some_account_items_social_media_account"),
        "some_account_items",
        ["social_media_account"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("some_account_items")
    op.drop_table("some_account_thumbnails")
    op.drop_table("some_accounts")
    op.drop_table("some_providers")
