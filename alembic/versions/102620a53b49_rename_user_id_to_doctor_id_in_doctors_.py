"""rename user_id to doctor_id in doctors table

Revision ID: 102620a53b49
Revises: 5814eba382b8
Create Date: 2025-05-13 15:38:04.579715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '102620a53b49'
down_revision: Union[str, None] = '5814eba382b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('doctors', 'user_id', new_column_name='doctor_id', existing_type=sa.Integer())


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('doctors', 'doctor_id', new_column_name='user_id', existing_type=sa.Integer())
