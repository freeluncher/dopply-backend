"""
create notifications table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240512_04_create_notifications'
down_revision = '20240512_03_create_records'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('from_patient_id', sa.Integer, sa.ForeignKey('patients.id'), nullable=False),
        sa.Column('to_doctor_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('record_id', sa.Integer, sa.ForeignKey('records.id'), nullable=False),
        sa.Column('status', sa.Enum('unread', 'read', name='notifstatus'), nullable=False)
    )

def downgrade():
    op.drop_table('notifications')
    sa.Enum(name='notifstatus').drop(op.get_bind(), checkfirst=False)
