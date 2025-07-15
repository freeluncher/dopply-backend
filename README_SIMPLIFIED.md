# Dopply Backend - Simplified Version

Backend API sederhana untuk aplikasi monitoring detak jantung janin, sesuai dengan kebutuhan di `FIX.md`.

## ✅ Perubahan Penyederhanaan

### File yang Dihapus:
- ❌ `fetal_legacy.py` - Legacy endpoints duplikat
- ❌ `fetal_monitoring_new.py` - Endpoint duplikat  
- ❌ `doctor_dashboard*.py` - Dashboard yang terlalu kompleks
- ❌ `fetal_monitoring_service.py` - Service yang terlalu rumit
- ❌ `patient_status_history.py` - Model yang tidak diperlukan
- ❌ File service duplikat lainnya

### Fitur yang Disederhanakan:
✅ **Authentication & JWT** - Login/register dengan role (patient, doctor, admin)  
✅ **Monitoring** - Submit dan ambil riwayat monitoring  
✅ **Doctor-Patient Management** - Dokter mengelola pasien  
✅ **Notifications** - Pasien share hasil ke dokter  
✅ **Admin** - Verifikasi dokter  
✅ **Local Time (WIB)** - Semua waktu menggunakan waktu lokal Indonesia  

## 📋 Endpoints Sesuai FIX.md

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register

### Monitoring (Main Feature)
- `POST /api/v1/monitoring/submit` - Submit hasil monitoring
- `GET /api/v1/monitoring/history` - Ambil riwayat monitoring

### Patient-Doctor Interaction  
- `POST /api/v1/monitoring/share` - Share monitoring ke dokter
- `GET /api/v1/monitoring/patients` - List pasien dokter
- `POST /api/v1/monitoring/patients/add` - Tambah pasien oleh dokter

### Notifications
- `GET /api/v1/monitoring/notifications` - Lihat notifikasi
- `POST /api/v1/monitoring/notifications/read/{id}` - Tandai notif dibaca

### Admin
- `POST /api/v1/monitoring/admin/verify-doctor` - Admin verifikasi dokter

## 🗂️ Struktur File Bersih

```
app/
├── main.py                           # FastAPI app sederhana
├── models/
│   └── medical.py                    # Model utama (User, Patient, Record, Notification, Doctor)
├── schemas/
│   ├── fetal_monitoring.py          # Schema monitoring
│   ├── user.py                      # Schema user
│   └── refresh.py                   # Schema refresh token
├── services/
│   ├── monitoring_simple.py         # Service utama monitoring
│   └── admin_doctor_validation_service.py
├── api/v1/endpoints/
│   ├── monitoring_simple.py         # Endpoint utama monitoring
│   ├── user.py                      # Auth endpoints
│   ├── admin_doctor_validation.py   # Admin endpoints
│   ├── patient_crud.py              # Patient CRUD
│   ├── token_verify.py              # Token verification
│   └── refresh.py                   # Refresh token
└── core/, db/                       # Config & database
```

## 🚀 Cara Menjalankan

1. **Setup environment**:
   ```bash
   cd dopply-backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Setup database**:
   - Update file `.env` dengan koneksi MySQL
   - Database akan auto-create tables saat start

3. **Jalankan server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Akses dokumentasi**:
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📱 Integrasi dengan Frontend Flutter

Sesuai tabel di `FIX.md`:

| Kegiatan                  | Frontend Call                        | Backend Endpoint                                  |
| ------------------------- | ------------------------------------ | ------------------------------------------------ |
| Login/Register            | POST `/auth/login`, `/auth/register` | ✅ Validasi user dan role                        |
| Monitoring selesai        | POST `/monitoring/submit`            | ✅ Klasifikasi dan simpan                        |
| Ambil riwayat monitoring  | GET `/monitoring/history`            | ✅ Filter berdasarkan user/role                  |
| Share hasil ke dokter     | POST `/monitoring/share`             | ✅ Update + notifikasi dokter                    |
| Lihat notifikasi          | GET `/monitoring/notifications`      | ✅ Dokter melihat notifikasi                     |
| Tandai notif dibaca       | POST `/monitoring/notifications/read/{id}` | ✅ Set `is_read = True`                    |
| Tambah pasien oleh dokter | POST `/monitoring/patients/add`      | ✅ Cek email pasien, buat relasi                 |
| List pasien dokter        | GET `/monitoring/patients`           | ✅ Hanya pasien terhubung                        |
| Admin verifikasi dokter   | POST `/monitoring/admin/verify-doctor` | ✅ Update `is_verified = True`                |

## 🔧 Perbaikan yang Dilakukan

1. **Konsistensi Penamaan**: Semua "bmp" diperbaiki menjadi "bpm"
2. **Pydantic V2 Compatibility**: Update config menggunakan `ConfigDict(from_attributes=True)`
3. **Single Service**: Satu service `MonitoringService` untuk semua fitur monitoring
4. **Simplified Models**: Model database hanya yang diperlukan sesuai FIX.md
5. **Clean Endpoints**: Satu endpoint file untuk semua fitur monitoring

## ⚡ Performa & Kesederhanaan

- 📉 **Mengurangi kompleksitas** dari 15+ service files menjadi 2 service files
- 📉 **Mengurangi endpoints** dari 10+ endpoint files menjadi 5 endpoint files  
- 📉 **Mengurangi schemas** dari 8+ schema files menjadi 3 schema files
- 🧹 **Clean Swagger Documentation**: Tag dan descriptions yang terorganisir
- ✅ **Fokus pada fitur inti** sesuai FIX.md tanpa fitur berlebihan
- ✅ **Mudah maintenance** dengan struktur yang bersih dan sederhana
