#!/usr/bin/env python3
"""
Script untuk mengelola migrasi database dengan mudah
Usage: 
  python manage_migrations.py status        # Check migration status
  python manage_migrations.py new "message" # Create new migration
  python manage_migrations.py apply         # Apply pending migrations
  python manage_migrations.py rollback      # Rollback last migration
  python manage_migrations.py history       # Show migration history
"""

import os
import sys
import argparse
from datetime import datetime
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_status():
    """Check current migration status"""
    print("🔍 Current Migration Status")
    print("=" * 40)
    
    # Show current migration
    print("📍 Current migration:")
    os.system("alembic current")
    
    # Show any pending migrations
    print("\n🔄 Pending migrations:")
    result = os.system("alembic check")
    if result == 0:
        print("✅ No pending migrations")
    
    # Show database tables
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text('SHOW TABLES'))
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📊 Database tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"  ✓ {table}")
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def create_migration(message):
    """Create new migration"""
    print(f"📝 Creating new migration: {message}")
    
    # Generate migration with auto-detection
    cmd = f'alembic revision --autogenerate -m "{message}"'
    result = os.system(cmd)
    
    if result == 0:
        print("✅ Migration created successfully")
        print("\n📋 Next steps:")
        print("1. Review the generated migration file")
        print("2. Test the migration: python manage_migrations.py apply")
        print("3. Verify the changes work correctly")
    else:
        print("❌ Failed to create migration")

def apply_migrations():
    """Apply all pending migrations"""
    print("🚀 Applying pending migrations...")
    
    result = os.system("alembic upgrade head")
    if result == 0:
        print("✅ All migrations applied successfully")
        check_status()
    else:
        print("❌ Failed to apply migrations")

def rollback_migration():
    """Rollback last migration"""
    print("⏪ Rolling back last migration...")
    
    # Get current migration
    result = os.system("alembic current")
    
    print("\n⚠️  This will rollback the last migration!")
    confirm = input("Are you sure? (y/N): ")
    
    if confirm.lower() == 'y':
        result = os.system("alembic downgrade -1")
        if result == 0:
            print("✅ Migration rolled back successfully")
            check_status()
        else:
            print("❌ Failed to rollback migration")
    else:
        print("❌ Rollback cancelled")

def show_history():
    """Show migration history"""
    print("📚 Migration History")
    print("=" * 40)
    
    os.system("alembic history --verbose")

def main():
    parser = argparse.ArgumentParser(description='Database migration management tool')
    parser.add_argument('action', choices=['status', 'new', 'apply', 'rollback', 'history'], 
                       help='Action to perform')
    parser.add_argument('message', nargs='?', help='Migration message (for new action)')
    
    args = parser.parse_args()
    
    if args.action == 'status':
        check_status()
    elif args.action == 'new':
        if not args.message:
            print("❌ Message required for new migration")
            print("Usage: python manage_migrations.py new 'Your migration message'")
            sys.exit(1)
        create_migration(args.message)
    elif args.action == 'apply':
        apply_migrations()
    elif args.action == 'rollback':
        rollback_migration()
    elif args.action == 'history':
        show_history()

if __name__ == "__main__":
    main()
