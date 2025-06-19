# Dopply Backend

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![Coverage Status](https://img.shields.io/badge/coverage-passing-brightgreen.svg)](https://pytest.org/)
[![License](https://img.shields.io/github/license/your-org/your-repo.svg)](LICENSE)

Dopply Backend adalah RESTful API berbasis FastAPI untuk aplikasi manajemen pasien, dokter, dan admin, dengan fitur monitoring, user management, dan pengaturan akun terintegrasi.

---

## Fitur Utama
- **Manajemen User**: CRUD untuk pasien, dokter, dan admin (dengan endpoint khusus admin)
- **Autentikasi JWT**: Login, proteksi endpoint, dan role-based access
- **Pengaturan Akun**: Endpoint unified untuk ganti email & password semua role
- **Monitoring**: Endpoint monitoring pasien & dokter
- **Integrasi Database**: Mendukung SQLite/MySQL (SQLAlchemy ORM)
- **Testing**: Suite pytest lengkap untuk integrasi dan unit test

## Struktur Project
```
app/
  main.py           # Entry point FastAPI
  api/v1/endpoints/ # Semua endpoint utama
  models/           # Model SQLAlchemy
  schemas/          # Pydantic schemas
  services/         # Business logic
  core/             # Security, config
  db/               # Session, seed, migrasi
alembic/            # Migrasi database
.env.example        # Contoh environment
requirements.txt    # Daftar dependensi
```

## Instalasi & Menjalankan
1. **Clone repo & buat virtualenv**
   ```bash
   git clone https://github.com/your-org/dopply-backend.git
   cd dopply-backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # atau
   source venv/bin/activate  # Linux/Mac
   ```
2. **Install dependensi**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy & edit .env**
   ```bash
   cp .env.example .env
   # Edit .env sesuai kebutuhan
   ```
4. **Jalankan migrasi database**
   ```bash
   alembic upgrade head
   ```
5. **Jalankan server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Testing
Jalankan semua test dengan:
```bash
pytest
```

## Konfigurasi Lingkungan
Lihat dan salin `.env.example` untuk konfigurasi yang dibutuhkan.

## Kontribusi
Pull request dan issue sangat diterima! Pastikan code sudah terformat dan semua test lulus.

## Lisensi
MIT

---

> Dopply Backend © 2025
