"""rename user_id to doctor_id in doctors table

Revision ID: rename_userid_to_doctorid
Revises: 1ea31430ddae
Create Date: 2025-05-13
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Rename column user_id to doctor_id in doctors table
    op.alter_column('doctors', 'user_id', new_column_name='doctor_id')

def downgrade():
    # Revert column doctor_id to user_id in doctors table
    op.alter_column('doctors', 'doctor_id', new_column_name='user_id')
