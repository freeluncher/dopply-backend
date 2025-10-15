# 🔍 **ANALISIS SKEMA DATABASE VS ENDPOINT REQUIREMENTS**

## ⚠️ **MASALAH YANG DITEMUKAN**

### 1. **Field Hilang di Model Database**

#### **Tabel `records` - Field BPM Statistik**
- ❌ **Missing**: `avg_bpm` (Integer) - Digunakan di endpoint `/results`
- ❌ **Missing**: `min_bpm` (Integer) - Digunakan di endpoint `/results` 
- ❌ **Missing**: `max_bpm` (Integer) - Digunakan di endpoint `/results`
- ❌ **Missing**: `duration_seconds` (Integer) - Digunakan di endpoint `/results`
- ❌ **Missing**: `shared_with_doctor_id` (Integer, FK ke users) - Digunakan untuk tracking sharing

#### **Field yang Ada tapi Berbeda Nama**
- ✅ **Ada**: `monitoring_duration` (Float) vs **Digunakan**: `duration_seconds` (Int)
- ✅ **Ada**: `shared_with` (Int, FK) vs **Digunakan**: `shared_with_doctor_id`

### 2. **Konflik Model Duplikat**
- ❌ **File Duplikat**: `medical.py` dan `medical_new.py` berisi model identik
- ⚠️ **Potensi Konflik**: `user.py` dikosongkan tapi masih ada

## 📋 **ENDPOINT REQUIREMENTS ANALYSIS**

### **Endpoint `/monitoring/results` (POST)**
**Input**: `MonitoringResultRequest`
```python
patientId: int
avgBpm: int        # ❌ Butuh kolom avg_bpm
minBpm: int        # ❌ Butuh kolom min_bpm  
maxBpm: int        # ❌ Butuh kolom max_bpm
duration: int      # ❌ Butuh kolom duration_seconds
dataPoints: List[int]  # ✅ Ada sebagai bpm_data (JSON)
timestamp: str     # ✅ Ada sebagai start_time
```

### **Endpoint `/monitoring/history` (GET)**
**Output**: Menggunakan field yang tidak ada di database
```python
"avgBpm": record.avg_bpm,          # ❌ Field tidak ada
"minBpm": record.min_bpm,          # ❌ Field tidak ada
"maxBpm": record.max_bpm,          # ❌ Field tidak ada  
"duration": record.duration_seconds, # ❌ Field tidak ada
"sharedWithDoctor": record.shared_with_doctor_id is not None # ❌ Field tidak ada
```

### **Endpoint `/monitoring/share` (POST)**
**Functionality**: Memerlukan tracking sharing status
```python
# Butuh field untuk tracking apakah record sudah dishare
shared_with_doctor_id: Optional[int]  # ❌ Field tidak ada
shared_at: Optional[datetime]         # ❌ Field tidak ada (opsional)
```

## 🔧 **SOLUSI YANG DIREKOMENDASIKAN**

### **1. Update Model Database**

#### **Tambah Field ke `records` Table**
```python
# Field BPM statistik
avg_bpm = Column(Integer, nullable=True)
min_bpm = Column(Integer, nullable=True)  
max_bpm = Column(Integer, nullable=True)
duration_seconds = Column(Integer, nullable=True)

# Field sharing tracking
shared_with_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
shared_at = Column(DateTime, nullable=True)
```

#### **Rename Field yang Ada**
```python
# Ganti monitoring_duration -> duration_minutes (untuk pembedaan)
duration_minutes = Column(Float, nullable=True)  # Untuk durasi dalam menit
duration_seconds = Column(Integer, nullable=True) # Untuk durasi dalam detik
```

### **2. Migration Script Required**
```sql
ALTER TABLE records ADD COLUMN avg_bpm INTEGER;
ALTER TABLE records ADD COLUMN min_bpm INTEGER;
ALTER TABLE records ADD COLUMN max_bpm INTEGER;
ALTER TABLE records ADD COLUMN duration_seconds INTEGER;
ALTER TABLE records ADD COLUMN shared_with_doctor_id INTEGER;
ALTER TABLE records ADD COLUMN shared_at DATETIME;

-- Add foreign key constraint
ALTER TABLE records ADD CONSTRAINT fk_records_shared_with_doctor 
  FOREIGN KEY (shared_with_doctor_id) REFERENCES users(id);
```

### **3. Cleanup Model Files**
- ❌ **Hapus**: `medical_new.py` (duplikat)
- ❌ **Hapus**: `user.py` (kosong, tidak digunakan)
- ✅ **Gunakan**: `medical.py` sebagai satu-satunya model

### **4. Update Service Layer**
Service layer perlu diadaptasi untuk:
- Menghitung `avg_bpm`, `min_bpm`, `max_bpm` dari `bpm_data` 
- Menyimpan `duration_seconds` dari request
- Handle sharing logic dengan field baru

## 🎯 **PRIORITAS IMPLEMENTASI**

### **HIGH PRIORITY**
1. ✅ Migration untuk menambah field BPM statistik
2. ✅ Update model `medical.py`  
3. ✅ Hapus file model duplikat
4. ✅ Update endpoint untuk menggunakan field yang benar

### **MEDIUM PRIORITY**  
1. ✅ Implementasi sharing tracking yang proper
2. ✅ Update service layer untuk konsistensi
3. ✅ Testing field compatibility

### **LOW PRIORITY**
1. ✅ Optimization performa query
2. ✅ Data validation tambahan
3. ✅ Documentation update

## ✅ **VALIDASI ENDPOINT SETELAH FIX**

### **Endpoint Test Cases**
1. **POST /monitoring/results** - Simpan data dengan BPM statistik
2. **GET /monitoring/history** - Ambil data dengan field lengkap
3. **POST /monitoring/share** - Test sharing functionality
4. **GET /monitoring/doctor-history** - Test doctor view dengan sharing status

### **Expected Behavior**
- Semua endpoint menggunakan field database yang konsisten
- Tidak ada error "field tidak ada" 
- Sharing functionality berfungsi dengan baik
- Data BPM statistik tersimpan dan terbaca dengan benar

---

**Status**: ⚠️ **REQUIRES IMMEDIATE ACTION**  
**Impact**: 🔴 **CRITICAL** - Endpoint tidak berfungsi dengan benar tanpa field ini