"""Remove fetal monitoring tables

Revision ID: remove_fetal_tables
Revises: 
Create Date: 2025-07-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'remove_fetal_tables'
down_revision = '692e6f2120e5'
branch_labels = None
depends_on = None

def upgrade():
    """Remove fetal monitoring specific tables since we'll use records table only"""
    
    # Drop fetal_monitoring_results table
    op.drop_table('fetal_monitoring_results')
    
    # Drop fetal_heart_rate_readings table  
    op.drop_table('fetal_heart_rate_readings')
    
    # Drop fetal_monitoring_sessions table
    op.drop_table('fetal_monitoring_sessions')
    
    print("✅ Fetal monitoring tables removed successfully")
    print("✅ System will now use 'records' table for all monitoring data")

def downgrade():
    """Recreate fetal monitoring tables if needed"""
    
    # Recreate fetal_monitoring_sessions
    op.create_table('fetal_monitoring_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('monitoring_type', sa.String(), nullable=False),
        sa.Column('gestational_age', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('doctor_notes', sa.Text(), nullable=True),
        sa.Column('shared_with_doctor', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate fetal_heart_rate_readings
    op.create_table('fetal_heart_rate_readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('bpm', sa.Integer(), nullable=False),
        sa.Column('signal_quality', sa.Float(), nullable=True),
        sa.Column('classification', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate fetal_monitoring_results
    op.create_table('fetal_monitoring_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('overall_classification', sa.String(), nullable=False),
        sa.Column('average_bpm', sa.Float(), nullable=False),
        sa.Column('baseline_variability', sa.Float(), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
