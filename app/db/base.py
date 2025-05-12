from app.db.session import Base
# Jangan import model di sini untuk menghindari circular import
# Model akan di-import langsung oleh Alembic/env.py saat migrasi

# Ensure Base is correctly imported and used for Alembic migrations.
