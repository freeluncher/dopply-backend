#!/usr/bin/env python3
"""
Script to check current database tables
"""

from app.core.config import settings
from sqlalchemy import create_engine, text

def check_tables():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text('SHOW TABLES'))
        tables = [row[0] for row in result.fetchall()]
        print('Current database tables:')
        for table in tables:
            print(f"  - {table}")

if __name__ == "__main__":
    check_tables()
