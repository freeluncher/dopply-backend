"""change records.doctor_id foreign key to doctors.doctor_id

Revision ID: 7958cb3b548e
Revises: 016b54aada15
Create Date: 2025-05-13 17:22:47.159265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7958cb3b548e'
down_revision: Union[str, None] = '016b54aada15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old foreign key constraint from records.doctor_id to users.id
    op.drop_constraint('records_ibfk_1', 'records', type_='foreignkey')
    # Create new foreign key from records.doctor_id to doctors.doctor_id
    op.create_foreign_key(
        'fk_records_doctor_id_doctors',
        'records', 'doctors',
        ['doctor_id'], ['doctor_id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new foreign key constraint
    op.drop_constraint('fk_records_doctor_id_doctors', 'records', type_='foreignkey')
    # Restore the old foreign key from records.doctor_id to users.id
    op.create_foreign_key(
        'records_ibfk_2',
        'records', 'users',
        ['doctor_id'], ['id'],
        ondelete='SET NULL'
    )
