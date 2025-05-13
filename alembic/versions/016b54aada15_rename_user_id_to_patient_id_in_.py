"""rename user_id to patient_id in patients table

Revision ID: 016b54aada15
Revises: 102620a53b49
Create Date: 2025-05-13 15:46:42.934530
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '016b54aada15'
down_revision = '102620a53b49'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('patients', 'user_id', new_column_name='patient_id', existing_type=sa.Integer())

def downgrade():
    op.alter_column('patients', 'patient_id', new_column_name='user_id', existing_type=sa.Integer())
