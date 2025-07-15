Berikut adalah **prompt full untuk pengembangan aplikasi Dopply**, mencakup:

* ✅ **Frontend Flutter (BLE, Auth, Dashboard, Monitoring, History, Role-based UI)**
* ✅ **Backend FastAPI (Auth JWT, Monitoring, Notifikasi, Relasi Dokter-Pasien)**
* ✅ **Integrasi antara frontend dan backend**
* ✅ **Fokus pada teknis, sesuai skripsi, clean architecture, dan modular**

Prompt ini **dipecah per modul** agar AI seperti GPT-4.1 atau GitHub Copilot dapat memahami dan mengeksekusi dengan akurat, tanpa kebingungan.

---

## ✅ Prompt Utama (Gabungan Frontend + Backend + Integrasi)

> 🎯 **Tujuan Prompt**: Saya ingin membuat aplikasi Android bernama **Dopply**, untuk monitoring detak jantung janin menggunakan ESP32 dan BLE. Aplikasi ini terdiri dari frontend Flutter dan backend FastAPI dengan database MySQL. Semua role user (pasien, dokter, admin) memiliki akses fitur berbeda. Gunakan waktu lokal Indonesia (WIB) dan struktur clean, modular, dan skripsi-friendly.

---

## 📁 Struktur Folder Project

```
dopply-project/
├── frontend/   # Flutter App
├── backend/    # FastAPI App
```

---

## 🔧 Backend Prompt – FastAPI (Letakkan di folder `backend/`)

### 🎯 Prompt untuk AI:

> Buatkan backend aplikasi monitoring detak jantung janin dengan **FastAPI** dan **MySQL**. Gunakan struktur modular dengan folder `routers`, `models`, `schemas`, `utils`, dan `database.py`. Gunakan JWT Auth dengan `python-jose`. Role user terdiri dari `pasien`, `dokter`, dan `admin`.

### ✅ Fitur yang harus diimplementasikan:

1. **Autentikasi dan Register + JWT**

   * Simpan role user
   * Dokter perlu diverifikasi admin
   * Persistent login (token 7 hari)

2. **Monitoring (oleh pasien atau dokter)**

   * Endpoint menerima data JSON list BPM
   * Backend klasifikasi (`normal`, `bradikardia`, `takikardia`)
   * Simpan hasil + catatan + waktu lokal (datetime.now())

3. **Manajemen Pasien (oleh dokter)**

   * Dokter bisa menambahkan pasien dengan email
   * Relasi dokter–pasien (tabel many-to-many)

4. **Riwayat Monitoring**

   * Pasien bisa lihat hasil sendiri
   * Dokter bisa lihat hasil pasien yang membagikan

5. **Notifikasi**

   * Pasien bisa membagikan hasil ke dokter
   * Notifikasi dibuat ke dokter
   * Dokter bisa melihat dan menandai sebagai "dibaca"

6. **Penghitungan Usia Kehamilan**

   * Simpan `hpht` pada pasien
   * Hitung usia kehamilan `(today - hpht) // 7`

7. **Admin**

   * Endpoint verifikasi dokter (update `is_verified = True`)

### 🧱 Struktur Folder Backend

```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── utils/
├── requirements.txt
├── .env
```

---

## 📱 Frontend Prompt – Flutter (Letakkan di folder `frontend/`)

### 🎯 Prompt untuk AI:

> Buatkan frontend Flutter untuk aplikasi Dopply, menggunakan **Riverpod** untuk state management, **dio** untuk API call, dan **flutter\_reactive\_ble** untuk BLE ESP32. Aplikasi memiliki role-based UI (pasien, dokter, admin), persistent login, dan fitur monitoring janin. Gunakan waktu lokal Indonesia dan `flutter_secure_storage` untuk menyimpan token.

### ✅ Fitur Frontend:

1. **Autentikasi (login/register)**

   * Simpan token JWT dan role
   * Persistent login saat buka ulang aplikasi
   * Redirect otomatis ke dashboard role

2. **Dashboard Role-Based**

   * Pasien: monitoring mandiri, riwayat, share ke dokter
   * Dokter: monitoring pasien, manajemen pasien, riwayat pasien, notifikasi
   * Admin: verifikasi dokter

3. **Monitoring via BLE**

   * Terima data dari ESP32 (UUID BLE)
   * Tampilkan grafik real-time
   * Setelah selesai → kirim data BPM ke backend

4. **Riwayat Monitoring**

   * Ambil dari backend
   * Tampilkan waktu, status, catatan, dan grafik

5. **Share Monitoring**

   * Pasien bisa membagikan hasil ke dokter terhubung

6. **Notifikasi**

   * Dokter menerima notifikasi dari pasien
   * Dokter bisa buka dan lihat detail monitoring

7. **Manajemen Pasien**

   * Dokter menambahkan pasien dengan email
   * Tampilkan daftar pasien

8. **Hitung Usia Kehamilan**

   * Tampilkan usia kehamilan pasien berdasarkan `hpht`

9. **Navigasi**

   * Gunakan `go_router` + dashboard/tabbar

### 📁 Struktur Folder Frontend

```
frontend/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── features/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── monitoring/
│   │   ├── history/
│   │   ├── notifications/
│   │   └── patient_management/
│   ├── services/
│   ├── providers/
│   ├── models/
│   ├── config/
│   └── routes/
```

---

## 🔁 Integrasi Frontend ⇄ Backend

| Kegiatan                  | Frontend                             | Backend Endpoint              |
| ------------------------- | ------------------------------------ | ----------------------------- |
| Login/Register            | POST `/auth/login`, `/auth/register` | Validasi user dan role        |
| Monitoring selesai        | POST `/monitoring/submit`            | Klasifikasi dan simpan        |
| Ambil riwayat monitoring  | GET `/monitoring/history`            | Filter berdasarkan user/role  |
| Share hasil ke dokter     | POST `/monitoring/share/{id}`        | Update + notifikasi dokter    |
| Lihat notifikasi          | GET `/notifications/`                | Dokter melihat notifikasi     |
| Tandai notif dibaca       | POST `/notifications/read/{id}`      | Set `is_read = True`          |
| Tambah pasien oleh dokter | POST `/patients/add`                 | Cek email pasien, buat relasi |
| List pasien dokter        | GET `/patients/`                     | Hanya pasien terhubung        |
| Admin verifikasi dokter   | POST `/admin/verify/{dokter_id}`     | Update `is_verified = True`   |

---

## 📌 Catatan Tambahan

* Gunakan **`datetime.now()`** tanpa timezone di backend (untuk waktu lokal)
* BLE hanya digunakan untuk **mengambil data di frontend**, bukan dikirim langsung ke backend
* Backend hanya menerima data **setelah monitoring selesai** (via Flutter POST)

---

Jika kamu ingin:

* ✅ File `README.md` lengkap (untuk repositori GitHub)
* ✅ Panduan deployment ke VM lokal/IDCloudHost
* ✅ Sample file `.env` dan `docker-compose` backend

Saya siap bantu selanjutnya! Mau lanjut dari bagian mana?
