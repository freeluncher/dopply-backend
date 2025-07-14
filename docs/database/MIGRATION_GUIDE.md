# Database Migration Guide

## Overview
This guide explains the structured database migration system for the Dopply Backend application.

# Database Migration Guide

## Overview
This guide explains the structured database migration system for the Dopply Backend application.

## Current Status ✅
- **Database State**: ✅ Fully synchronized with models
- **Migration Head**: `692e6f2120e5` (Remove unused status fields from doctor_patient)
- **All Tables**: 12 tables successfully migrated and tracked

## Migration Structure

### 001_initial_schema
**Purpose**: Core foundational tables
- `users` - User accounts (admin, doctor, patient)
- `patients` - Patient profiles
- `doctors` - Doctor validation status
- `doctor_patient` - Doctor-patient associations

### 002_records_notifications  
**Purpose**: Medical records and notification system
- `records` - Medical monitoring records
- `notifications` - Doctor-patient notifications

### 003_patient_status_history
**Purpose**: Patient status audit trail
- `patient_status_history` - Track patient status changes

### 004_fetal_monitoring
**Purpose**: Fetal monitoring system
- `fetal_monitoring_sessions` - Monitoring sessions
- `fetal_heart_rate_readings` - Heart rate data
- `fetal_monitoring_results` - Analysis results
- `pregnancy_info` - Pregnancy information

### 692e6f2120e5_remove_unused_status_fields_from_doctor_patient
**Purpose**: Database cleanup
- Removed unused `status_updated_at` and `status_updated_by` fields from `doctor_patient` table

## How to Use

### Quick Commands
```bash
# Check current status
python manage_migrations.py status

# Create new migration
python manage_migrations.py new "Description of changes"

# Apply pending migrations
python manage_migrations.py apply

# Show migration history
python manage_migrations.py history
```

### Advanced Commands
```bash
# Check if database is in sync
alembic check

# Show current migration
alembic current

# Manual migration upgrade
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Full Reset (if needed)
```bash
# Complete database reset and rebuild
python full_reset.py

# Or structured reset
python reset_migrations.py
```

## Best Practices

### 1. Naming Conventions
- Use descriptive names: `001_initial_schema`, `002_add_user_preferences`
- Include sequence numbers for easy tracking
- Use snake_case for consistency

### 2. Migration Safety
- Always backup database before major migrations
- Test migrations on development environment first
- Include proper rollback procedures in `downgrade()`

### 3. Model-Migration Sync
- Keep SQLAlchemy models and migrations in sync
- Use `alembic revision --autogenerate` for model changes
- Review generated migrations before applying

### 4. Data Migrations
- Create separate migrations for data changes
- Use raw SQL or SQLAlchemy Core for data operations
- Test data migrations thoroughly

## Troubleshooting

### Common Issues

**Migration conflict/branching**
```bash
# Check for branch points
alembic branches

# Merge branches
alembic merge [revisions] -m "merge message"
```

**Database out of sync**
```bash
# Reset to clean state
python reset_migrations.py

# Or manually stamp current state
alembic stamp head
```

**Failed migration**
```bash
# Check current state
alembic current

# Rollback to previous working state
alembic downgrade [previous_revision]

# Fix migration file and retry
alembic upgrade head
```

## Migration File Template

```python
"""Description of migration

Revision ID: xxx_descriptive_name
Revises: previous_revision
Create Date: YYYY-MM-DD HH:MM:SS.ffffff

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxx_descriptive_name'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Forward migration operations
    pass

def downgrade():
    # Reverse migration operations
    pass
```

## Database Schema Overview

### Core Tables
- **users**: User authentication and profiles
- **patients**: Patient medical profiles
- **doctors**: Doctor validation status
- **doctor_patient**: Many-to-many doctor-patient relationships

### Medical Records
- **records**: Medical monitoring records
- **notifications**: Communication between doctors and patients

### Audit & History
- **patient_status_history**: Track patient status changes

### Fetal Monitoring
- **fetal_monitoring_sessions**: Monitoring sessions
- **fetal_heart_rate_readings**: Raw heart rate data
- **fetal_monitoring_results**: Analysis and recommendations
- **pregnancy_info**: Pregnancy-related information

## Environment Variables
Make sure these are set in your environment:
- `DATABASE_URL`: MySQL connection string
- Other app configuration as needed

## Support
For issues or questions about migrations:
1. Check this documentation
2. Review migration history: `alembic history`
3. Check database state: `python check_tables.py`
4. Use reset script if needed: `python reset_migrations.py`
