"""Add records and notifications

Revision ID: 002_records_notifications
Revises: 001_initial_schema
Create Date: 2024-01-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002_records_notifications'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None

def upgrade():
    # Create records table
    op.create_table('records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('source', sa.Enum('clinic', 'self', name='recordsource'), nullable=False),
    sa.Column('bpm_data', sa.JSON(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('classification', sa.String(length=255), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('shared_with', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['shared_with'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_records_id'), 'records', ['id'], unique=False)

    # Create notifications table
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_patient_id', sa.Integer(), nullable=False),
    sa.Column('to_doctor_id', sa.Integer(), nullable=False),
    sa.Column('record_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('unread', 'read', name='notificationstatus'), nullable=False),
    sa.ForeignKeyConstraint(['from_patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['record_id'], ['records.id'], ),
    sa.ForeignKeyConstraint(['to_doctor_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_records_id'), table_name='records')
    op.drop_table('records')
