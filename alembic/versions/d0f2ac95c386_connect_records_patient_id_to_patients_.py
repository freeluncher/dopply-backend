"""connect records.patient_id to patients.id

Revision ID: d0f2ac95c386
Revises: 634f725d2fa3
Create Date: 2025-05-15 22:53:47.478059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd0f2ac95c386'
down_revision: Union[str, None] = '634f725d2fa3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old foreign key if exists (adjust constraint name as needed)
    with op.batch_alter_table('records') as batch_op:
        batch_op.drop_constraint('fk_records_patient_id_patients', type_='foreignkey')
        # Tambahkan foreign key baru ke patients.id
        batch_op.create_foreign_key(
            'fk_records_patient_id_patients_id',
            'patients',
            ['patient_id'], ['id'],
            ondelete='CASCADE'
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('records') as batch_op:
        batch_op.drop_constraint('fk_records_patient_id_patients_id', type_='foreignkey')
        # Restore old constraint if needed (adjust as needed)
        batch_op.create_foreign_key(
            'fk_records_patient_id_patients',
            'patients',
            ['patient_id'], ['patient_id'],
            ondelete='CASCADE'
        )
