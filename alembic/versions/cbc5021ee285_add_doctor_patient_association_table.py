"""add doctor_patient association table

Revision ID: cbc5021ee285
Revises: 6ebd02770d6d
Create Date: 2025-05-15 18:55:54.736022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'cbc5021ee285'
down_revision: Union[str, None] = '6ebd02770d6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Only create the doctor_patient association table
    op.create_table(
        'doctor_patient',
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('doctors.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id', ondelete='CASCADE'), primary_key=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('doctor_patient')
