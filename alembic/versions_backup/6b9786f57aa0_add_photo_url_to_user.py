"""add photo_url to user

Revision ID: 6b9786f57aa0
Revises: ab7d7a1e6bfc
Create Date: 2025-06-30 06:28:42.347569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b9786f57aa0'
down_revision: Union[str, None] = 'ab7d7a1e6bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('photo_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'photo_url')
