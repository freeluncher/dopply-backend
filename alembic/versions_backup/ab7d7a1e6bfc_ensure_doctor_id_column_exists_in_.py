"""Ensure doctor_id column exists in records

Revision ID: ab7d7a1e6bfc
Revises: d0f2ac95c386
Create Date: 2025-06-30 04:42:48.122038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ab7d7a1e6bfc'
down_revision: Union[str, None] = 'd0f2ac95c386'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Kolom doctor_id sudah ada, hanya tambahkan foreign key jika perlu
    with op.batch_alter_table('records') as batch_op:
        batch_op.create_foreign_key('fk_records_doctor_id_users', 'users', ['doctor_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('records') as batch_op:
        batch_op.drop_constraint('fk_records_doctor_id_users', type_='foreignkey')
