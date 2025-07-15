# 🌱 Database Seeding Guide

## 📋 Overview
Script untuk menambahkan user test ke database Dopply untuk development dan testing.

## 🎯 Test Users yang Dibuat

| Role | Email | Password | Status |
|------|-------|----------|--------|
| 👨‍⚕️ **Doctor** | `dokter@gmail.com` | `password123` | ✅ Verified |
| 👤 **Patient** | `pasien@gmail.com` | `password123` | ✅ Active |
| 👨‍💼 **Admin** | `admin@gmail.com` | `password123` | ✅ Active |

## 🚀 Quick Start

### 1. Seed Database
```bash
# Option 1: Simple seeding
python seed.py

# Option 2: Detailed seeding with checks
python scripts/seed_users.py
```

### 2. Test Login Credentials
```bash
python test_login.py
```

### 3. Check Existing Users
```bash
python -c "from scripts.seed_users import check_existing_users; check_existing_users()"
```

## 📁 Files Created

- `scripts/seed_users.py` - Main seeding script with detailed functions
- `seed.py` - Simple wrapper script for quick seeding
- `test_login.py` - Login credential testing script

## 🔍 What Gets Created

### Doctor User
- **Name**: "Dr. Dokter Test"
- **Email**: dokter@gmail.com
- **Role**: doctor
- **Specialization**: "Obstetri & Ginekologi"
- **Verified**: ✅ True (ready to use)

### Patient User + Patient Record
- **User Name**: "Pasien Test"
- **Email**: pasien@gmail.com  
- **Role**: patient
- **Patient Record**: Automatically created with HPHT for testing

### Admin User
- **Name**: "Admin Test"
- **Email**: admin@gmail.com
- **Role**: admin

## 🛡️ Safety Features

- ✅ **Duplicate Protection**: Won't create users if they already exist
- ✅ **Error Handling**: Rollback on errors
- ✅ **Password Hashing**: Uses Argon2 for secure password storage
- ✅ **Local Time**: Uses Indonesia timezone for timestamps

## 🧪 Testing the Setup

### Test API Endpoints
```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dokter@gmail.com", 
    "password": "password123"
  }'

# Test with patient
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "pasien@gmail.com", 
    "password": "password123"
  }'
```

### Expected Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Dr. Dokter Test",
    "email": "dokter@gmail.com", 
    "role": "doctor",
    "is_verified": true
  }
}
```

## 🔄 Re-seeding

If you need to reset and reseed:

```bash
# 1. Drop and recreate database (if needed)
# Or delete specific users from database

# 2. Run seeding again
python seed.py
```

## 📊 Production Notes

⚠️ **IMPORTANT**: These are test users for development only!

- **Never use in production**
- **Change default passwords**
- **Remove test data before deployment**

## 🎯 Usage in Development

### Frontend Testing
```javascript
// Login test data
const testCredentials = {
  doctor: { email: 'dokter@gmail.com', password: 'password123' },
  patient: { email: 'pasien@gmail.com', password: 'password123' },
  admin: { email: 'admin@gmail.com', password: 'password123' }
}
```

### Backend Testing
```python
# In test files
TEST_DOCTOR_EMAIL = "dokter@gmail.com"
TEST_PATIENT_EMAIL = "pasien@gmail.com" 
TEST_PASSWORD = "password123"
```

---

**Status**: ✅ **READY FOR DEVELOPMENT**  
**Created**: July 15, 2025  
**Users**: 3 test users (doctor, patient, admin)
