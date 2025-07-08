# Scripts Organization

This directory contains organized scripts for database management, seeding, and validation.

## Folder Structure

### 📁 `database/`
Database management and migration scripts:
- Database reset and migration utilities
- Alembic management tools

### 📁 `seeding/`
Data seeding and population scripts:
- `seed_database.py` - Main comprehensive seeding script
- `efficient_seeding.py` - Batch processing seeding
- `complete_missing_data.py` - Add missing table data
- `add_fetal_monitoring.py` - Add fetal monitoring data
- `reseed_records.py` / `reseed_records_fixed.py` - Record reseeding utilities

### 📁 `validation/`
Database validation and checking scripts:
- `final_database_check.py` - Comprehensive database verification
- `detailed_check.py` - Detailed table status check
- `check_seeded_data.py` - Basic data verification
- `check_fetal_tables.py` - Fetal monitoring data check
- `check_empty_tables.py` - Empty table detection
- `validate_records.py` / `validate_system.py` - System validation

### 📁 `utils/`
Utility scripts:
- `delete_pycache.py` - Clean Python cache files

## Usage

### Running Scripts from Project Root

Since scripts are now in subdirectories, run them from the project root using:

```bash
# Seeding
python scripts/seeding/seed_database.py
python scripts/seeding/complete_missing_data.py

# Validation
python scripts/validation/final_database_check.py
python scripts/validation/detailed_check.py

# Database Management
python scripts/database/full_reset.py
python scripts/database/reset_migrations.py

# Utils
python scripts/utils/delete_pycache.py
```

### Quick Commands

**Seed Database:**
```bash
python scripts/seeding/seed_database.py
```

**Check Database Status:**
```bash
python scripts/validation/final_database_check.py
```

**Reset Database:**
```bash
python scripts/database/full_reset.py
```

## Notes

- All scripts maintain their original functionality
- Path imports are handled automatically
- Scripts can be run from the project root directory
- Each folder contains related functionality for easier maintenance
