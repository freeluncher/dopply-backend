"""Add patient status history

Revision ID: 003_patient_status_history
Revises: 002_records_notifications
Create Date: 2024-01-01 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '003_patient_status_history'
down_revision = '002_records_notifications'
branch_labels = None
depends_on = None

def upgrade():
    # Create patient_status_history table
    op.create_table('patient_status_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('old_status', sa.String(length=50), nullable=True),
    sa.Column('new_status', sa.String(length=50), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('changed_by', sa.Integer(), nullable=False),
    sa.Column('changed_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('patient_status_history')
