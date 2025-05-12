"""
create records table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240512_03_create_records'
down_revision = '20240512_02_create_patients'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'records',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('patient_id', sa.Integer, sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('doctor_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('source', sa.Enum('clinic', 'self', name='recordsource'), nullable=False),
        sa.Column('bpm_data', sa.JSON, nullable=True),
        sa.Column('start_time', sa.DateTime, nullable=False),
        sa.Column('end_time', sa.DateTime, nullable=True),
        sa.Column('classification', sa.String(255), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('shared_with', sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    )

def downgrade():
    op.drop_table('records')
    sa.Enum(name='recordsource').drop(op.get_bind(), checkfirst=False)
