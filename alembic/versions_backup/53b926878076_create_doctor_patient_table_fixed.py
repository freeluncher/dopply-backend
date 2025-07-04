"""create_doctor_patient_table_fixed

Revision ID: 53b926878076
Revises: 4ffe8a362f21
Create Date: 2025-07-03 00:19:53.075027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53b926878076'
down_revision: Union[str, None] = '4ffe8a362f21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create doctor_patient table with correct foreign keys."""
    # Create doctor_patient table with proper foreign key relationships
    op.create_table(
        'doctor_patient',
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('patient_id', sa.Integer(), sa.ForeignKey('patients.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    )


def downgrade() -> None:
    """Drop doctor_patient table."""
    op.drop_table('doctor_patient')
