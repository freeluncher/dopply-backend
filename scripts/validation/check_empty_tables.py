from app.core.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    
    # Get all tables
    result = conn.execute(text('SHOW TABLES'))
    all_tables = [row[0] for row in result.fetchall()]
    
    # Check each table
    empty_tables = []
    filled_tables = []
    
    for table in all_tables:
        if table != 'alembic_version':
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.fetchone()[0]
                if count == 0:
                    empty_tables.append(table)
                else:
                    filled_tables.append((table, count))
            except Exception as e:
                print(f"Error checking {table}: {e}")

print("📊 Database Status:")
print(f"✅ Tables with data ({len(filled_tables)}):")
for table, count in filled_tables:
    print(f"  - {table}: {count} records")

print(f"\n⚪ Empty tables ({len(empty_tables)}):")
for table in empty_tables:
    print(f"  - {table}")
