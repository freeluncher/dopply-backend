"""connect records.patient_id to patients.patient_id

Revision ID: 6ebd02770d6d
Revises: 7958cb3b548e
Create Date: 2025-05-13 17:31:15.901625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ebd02770d6d'
down_revision: Union[str, None] = '7958cb3b548e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Tambahkan foreign key dari records.patient_id ke patients.patient_id
    op.create_foreign_key(
        'fk_records_patient_id_patients',
        'records', 'patients',
        ['patient_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Hapus foreign key dari records.patient_id ke patients.patient_id
    op.drop_constraint('fk_records_patient_id_patients', 'records', type_='foreignkey')
