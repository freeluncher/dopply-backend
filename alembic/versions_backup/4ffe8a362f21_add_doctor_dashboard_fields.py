"""add_doctor_dashboard_fields

Revision ID: 4ffe8a362f21
Revises: 6b9786f57aa0
Create Date: 2025-07-02 23:43:14.034243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '4ffe8a362f21'
down_revision: Union[str, None] = '6b9786f57aa0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add doctor dashboard fields."""
    
    # Add new columns to users table if they don't exist
    with op.batch_alter_table('users', schema=None) as batch_op:
        # photo_url already exists from previous migration, so skip it
        
        # Check and add created_at column
        try:
            batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        except Exception:
            pass  # Column might already exist
    
    # Add new columns to patients table if they don't exist
    with op.batch_alter_table('patients', schema=None) as batch_op:
        try:
            batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))
        except Exception:
            pass
        
        try:
            batch_op.add_column(sa.Column('gender', sa.String(10), nullable=True))
        except Exception:
            pass
        
        try:
            batch_op.add_column(sa.Column('phone', sa.String(20), nullable=True))
        except Exception:
            pass
        
        # Change patient_id back to user_id to match our models
        # Based on migration history, the column is currently named patient_id but should be user_id
        try:
            batch_op.alter_column('patient_id', 
                                new_column_name='user_id',
                                existing_type=sa.Integer(),
                                nullable=False)
        except Exception:
            pass  # Column might already be named correctly
    
    # Add updated_at column to doctor_patient table if it doesn't exist
    with op.batch_alter_table('doctor_patient', schema=None) as batch_op:
        try:
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True, 
                                        server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')))
        except Exception:
            pass
    
    # Update foreign key constraints in doctor_patient table
    # Based on migration history, doctor_patient references doctors.doctor_id and patients.patient_id
    # But our model expects doctors.doctor_id and patients.id
    # We need to update the patient_id constraint only
    
    try:
        # Drop existing foreign key constraint for patient_id that references patients.patient_id
        op.drop_constraint('doctor_patient_ibfk_2', 'doctor_patient', type_='foreignkey')
        # Add new foreign key constraint pointing to patients.id instead of patients.patient_id
        op.create_foreign_key('fk_doctor_patient_patient_id', 'doctor_patient', 'patients', ['patient_id'], ['id'], ondelete='CASCADE')
    except Exception:
        pass
    
    # Doctor foreign key should already be correct (doctors.doctor_id), but let's ensure it
    try:
        # Check if we need to update doctor foreign key constraint name for consistency
        op.drop_constraint('doctor_patient_ibfk_1', 'doctor_patient', type_='foreignkey')
        # Recreate with consistent naming
        op.create_foreign_key('fk_doctor_patient_doctor_id', 'doctor_patient', 'doctors', ['doctor_id'], ['doctor_id'], ondelete='CASCADE')
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema - Remove doctor dashboard fields."""
    
    # Restore foreign key constraints in doctor_patient table
    try:
        # Drop new foreign key constraints
        op.drop_constraint('fk_doctor_patient_doctor_id', 'doctor_patient', type_='foreignkey')
        op.drop_constraint('fk_doctor_patient_patient_id', 'doctor_patient', type_='foreignkey')
        
        # Restore original constraints
        op.create_foreign_key('doctor_patient_ibfk_1', 'doctor_patient', 'doctors', ['doctor_id'], ['doctor_id'], ondelete='CASCADE')
        op.create_foreign_key('doctor_patient_ibfk_2', 'doctor_patient', 'patients', ['patient_id'], ['patient_id'], ondelete='CASCADE')
    except Exception:
        pass
    
    # Remove new columns from users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        try:
            batch_op.drop_column('created_at')
        except Exception:
            pass
        # Don't remove photo_url as it was added in previous migration
    
    # Remove new columns from patients table
    with op.batch_alter_table('patients', schema=None) as batch_op:
        try:
            batch_op.drop_column('phone')
        except Exception:
            pass
        
        try:
            batch_op.drop_column('gender')
        except Exception:
            pass
        
        try:
            batch_op.drop_column('age')
        except Exception:
            pass
        
        # Rename user_id back to patient_id if it was renamed
        try:
            batch_op.alter_column('user_id', 
                                new_column_name='patient_id',
                                existing_type=sa.Integer(),
                                nullable=False)
        except Exception:
            pass
    
    # Remove updated_at column from doctor_patient table
    with op.batch_alter_table('doctor_patient', schema=None) as batch_op:
        try:
            batch_op.drop_column('updated_at')
        except Exception:
            pass
