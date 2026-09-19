"""make bureau central link fields nullable on bureaux_vote

Revision ID: d5fbabc5576b
Revises: 0887a263802c
Create Date: 2026-09-19 19:23:57.065980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd5fbabc5576b'
down_revision: Union[str, None] = '0887a263802c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # batch mode required for SQLite (no native ALTER COLUMN); also works on PostgreSQL
    with op.batch_alter_table("bureaux_vote") as batch_op:
        batch_op.alter_column(
            "numero_bureau_central", existing_type=sa.VARCHAR(length=50), nullable=True
        )
        batch_op.alter_column(
            "president_bureau_central", existing_type=sa.VARCHAR(length=255), nullable=True
        )


def downgrade() -> None:
    with op.batch_alter_table("bureaux_vote") as batch_op:
        batch_op.alter_column(
            "president_bureau_central", existing_type=sa.VARCHAR(length=255), nullable=False
        )
        batch_op.alter_column(
            "numero_bureau_central", existing_type=sa.VARCHAR(length=50), nullable=False
        )
