"""
create patients table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240512_02_create_patients'
down_revision = '20240512_01_create_users'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'patients',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('address', sa.String(255), nullable=True),
        sa.Column('medical_note', sa.Text, nullable=True)
    )

def downgrade():
    op.drop_table('patients')
