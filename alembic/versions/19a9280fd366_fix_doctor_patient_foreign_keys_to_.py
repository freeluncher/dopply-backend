"""fix doctor_patient foreign keys to doctor_id and patient_id

Revision ID: 19a9280fd366
Revises: cbc5021ee285
Create Date: 2025-05-15 19:02:37.376698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '19a9280fd366'
down_revision: Union[str, None] = 'cbc5021ee285'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old doctor_patient table if exists
    op.drop_table('doctor_patient')
    # Create new doctor_patient table with correct FKs
    op.create_table(
        'doctor_patient',
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('doctors.doctor_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.patient_id', ondelete='CASCADE'), primary_key=True)
    )


def downgrade() -> None:
    op.drop_table('doctor_patient')
