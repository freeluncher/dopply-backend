"""Initial comprehensive schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # 1. Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('admin', 'doctor', 'patient', name='userrole'), nullable=False),
    sa.Column('photo_url', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Create patients table
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('medical_note', sa.Text(), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)

    # 3. Create doctors table
    op.create_table('doctors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('is_valid', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('doctor_id')
    )
    op.create_index(op.f('ix_doctors_id'), 'doctors', ['id'], unique=False)

    # 4. Create doctor_patient association table
    op.create_table('doctor_patient',
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('assigned_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('status_updated_at', sa.DateTime(), nullable=True),
    sa.Column('status_updated_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['status_updated_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('doctor_id', 'patient_id')
    )


def downgrade():
    op.drop_table('doctor_patient')
    op.drop_index(op.f('ix_doctors_id'), table_name='doctors')
    op.drop_table('doctors')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_table('patients')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
