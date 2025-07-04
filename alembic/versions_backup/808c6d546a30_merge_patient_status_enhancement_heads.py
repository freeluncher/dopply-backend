"""merge patient status enhancement heads

Revision ID: 808c6d546a30
Revises: 20250703_patient_status_enhancement, 72260757028e
Create Date: 2025-07-03 10:18:44.164942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '808c6d546a30'
down_revision: Union[str, None] = ('20250703_patient_status_enhancement', '72260757028e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
