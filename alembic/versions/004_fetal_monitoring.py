"""Add fetal monitoring system

Revision ID: 004_fetal_monitoring
Revises: 003_patient_status_history
Create Date: 2024-01-01 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '004_fetal_monitoring'
down_revision = '003_patient_status_history'
branch_labels = None
depends_on = None

def upgrade():
    # Create fetal_monitoring_sessions table
    op.create_table('fetal_monitoring_sessions',
    sa.Column('id', sa.String(length=50), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('monitoring_type', sa.Enum('clinic', 'home', name='monitoringtype'), nullable=False),
    sa.Column('gestational_age', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('doctor_notes', sa.Text(), nullable=True),
    sa.Column('shared_with_doctor', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fetal_monitoring_sessions_id'), 'fetal_monitoring_sessions', ['id'], unique=False)

    # Create fetal_heart_rate_readings table
    op.create_table('fetal_heart_rate_readings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=50), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('bpm', sa.Integer(), nullable=False),
    sa.Column('signal_quality', sa.Float(), nullable=True),
    sa.Column('classification', sa.Enum('normal', 'bradycardia', 'tachycardia', 'irregular', name='fetalclassification'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['fetal_monitoring_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fetal_heart_rate_readings_id'), 'fetal_heart_rate_readings', ['id'], unique=False)

    # Create fetal_monitoring_results table
    op.create_table('fetal_monitoring_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.String(length=50), nullable=False),
    sa.Column('overall_classification', sa.Enum('normal', 'concerning', 'abnormal', name='overallclassification'), nullable=False),
    sa.Column('average_bpm', sa.Float(), nullable=False),
    sa.Column('baseline_variability', sa.Float(), nullable=True),
    sa.Column('findings', sa.JSON(), nullable=True),
    sa.Column('recommendations', sa.JSON(), nullable=True),
    sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='risklevel'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['fetal_monitoring_sessions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_fetal_monitoring_results_id'), 'fetal_monitoring_results', ['id'], unique=False)

    # Create pregnancy_info table
    op.create_table('pregnancy_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('gestational_age', sa.Integer(), nullable=False),
    sa.Column('last_menstrual_period', sa.Date(), nullable=True),
    sa.Column('expected_due_date', sa.Date(), nullable=True),
    sa.Column('is_high_risk', sa.Boolean(), nullable=False),
    sa.Column('complications', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pregnancy_info_id'), 'pregnancy_info', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_pregnancy_info_id'), table_name='pregnancy_info')
    op.drop_table('pregnancy_info')
    op.drop_index(op.f('ix_fetal_monitoring_results_id'), table_name='fetal_monitoring_results')
    op.drop_table('fetal_monitoring_results')
    op.drop_index(op.f('ix_fetal_heart_rate_readings_id'), table_name='fetal_heart_rate_readings')
    op.drop_table('fetal_heart_rate_readings')
    op.drop_index(op.f('ix_fetal_monitoring_sessions_id'), table_name='fetal_monitoring_sessions')
    op.drop_table('fetal_monitoring_sessions')
