"""convert doctor_patient to association object with attributes

Revision ID: 634f725d2fa3
Revises: 19a9280fd366
Create Date: 2025-05-15 19:20:04.490987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '634f725d2fa3'
down_revision: Union[str, None] = '19a9280fd366'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop old doctor_patient table if exists
    op.drop_table('doctor_patient')
    # Create new doctor_patient association object table
    op.create_table(
        'doctor_patient',
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('doctors.doctor_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.patient_id', ondelete='CASCADE'), primary_key=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('doctor_patient')
