"""Add admin user

Revision ID: be7f86ca4fe0
Revises: 0bf12f026156
Create Date: 2025-05-12 05:17:54.545041

"""
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


# revision identifiers, used by Alembic.
revision: str = 'be7f86ca4fe0'
down_revision: Union[str, None] = '0bf12f026156'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    db: Session = SessionLocal()
    hashed_password = get_password_hash("admin123")
    admin_user = User(
        username="admin",
        email="admin@dopply.my.id",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True
    )
    db.add(admin_user)
    db.commit()
    db.close()


def downgrade() -> None:
    """Downgrade schema."""
    pass
