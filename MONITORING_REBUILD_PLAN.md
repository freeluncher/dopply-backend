# 🔄 PLAN PENGHAPUSAN DAN REBUILD FITUR MONITORING
*Complete Removal and Rebuild Plan for Fetal Monitoring Features*

## 📋 OVERVIEW

### Tujuan:
1. **Hapus** semua fitur monitoring lama (dokter dan pasien)
2. **Rebuild** dengan flow baru menggunakan **hanya tabel `records`**
3. **Pertahankan** semua fitur lain (UI tidak berubah)

### Flow Baru:

#### 🏥 **Monitoring oleh Dokter:**
1. Dokter pilih pasien yang sudah terassign
2. Dokter connect ke ESP32  
3. Dokter start monitoring → data dari ESP32
4. Dokter stop monitoring → data ke backend untuk klasifikasi
5. Backend return hasil klasifikasi
6. Dokter tambah notes
7. Dokter simpan hasil monitoring
8. Hasil bisa dilihat di riwayat

#### 👤 **Monitoring Mandiri Pasien:**
1. Pasien connect ke ESP32
2. Pasien start monitoring → data dari ESP32  
3. Pasien stop monitoring → data ke backend untuk klasifikasi
4. Backend return hasil klasifikasi
5. Pasien simpan hasil monitoring
6. Hasil bisa dilihat di riwayat & dibagikan ke dokter

---

## 🗑️ FASE 1: PENGHAPUSAN FITUR LAMA

### Backend - Files to Remove/Modify:

#### A. Remove Endpoints (dari `fetal_monitoring.py`):
```python
# HAPUS endpoints ini:
- POST /api/v1/fetal-monitoring/sessions
- GET /api/v1/fetal-monitoring/sessions
- GET /api/v1/fetal-monitoring/sessions/{session_id}
- PUT /api/v1/fetal-monitoring/sessions/{session_id}/share
- POST /api/v1/fetal-monitoring/classify
- POST /api/v1/fetal-monitoring/pregnancy-info
- GET /api/v1/fetal-monitoring/pregnancy-info/{patient_id}
- PUT /api/v1/fetal-monitoring/pregnancy-info/{patient_id}
```

#### B. Remove dari `doctor_dashboard.py`:
```python
# HAPUS endpoints ini:
- GET /patients/{patient_id}/monitoring/history
```

#### C. Clean Up Service Methods:
```python
# HAPUS methods dari FetalMonitoringService:
- save_monitoring_session (lama)
- get_monitoring_sessions (lama)  
- get_monitoring_session (lama)
- share_session_with_doctor (lama)
- create_pregnancy_info
- get_pregnancy_info
- update_pregnancy_info
```

#### D. Remove Schemas:
```python
# HAPUS dari fetal_monitoring.py schemas:
- FetalMonitoringSessionCreate
- FetalMonitoringSessionResponse
- FetalMonitoringSessionList
- ShareSessionRequest
- ShareSessionResponse
- PregnancyInfoCreate
- PregnancyInfoUpdate
- PregnancyInfoResponse
- Semua schemas kompleks lama
```

---

## 🏗️ FASE 2: REBUILD FITUR BARU

### Backend - New Structure:

#### A. New Schemas (`app/schemas/fetal_monitoring.py`):
```python
# BARU - Simplified schemas
class ESP32MonitoringRequest(BaseModel):
    patient_id: int
    gestational_age: int
    bpm_readings: List[int]  # Raw BPM dari ESP32
    monitoring_duration: Optional[float] = None  # dalam menit
    notes: Optional[str] = None

class ESP32MonitoringResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]  # Classification result + record info

class MonitoringClassificationResult(BaseModel):
    classification: str  # "normal", "bradycardia", "tachycardia", "irregular"
    average_bpm: float
    risk_level: str  # "low", "medium", "high"
    recommendations: List[str]
    variability: float
    
class MonitoringHistoryResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]  # Records dari database
    total_count: int
    
class ShareMonitoringRequest(BaseModel):
    record_id: int
    doctor_id: int
    notes: Optional[str] = None
```

#### B. New Service Methods (`app/services/fetal_monitoring_service.py`):
```python
# BARU - Simplified methods using only records table

@staticmethod
def process_esp32_monitoring(db, request: ESP32MonitoringRequest, user_id: int, user_role: str) -> Dict[str, Any]:
    """Process ESP32 monitoring data and save to records table"""
    
@staticmethod  
def get_monitoring_history(db, patient_id: Optional[int] = None, doctor_id: Optional[int] = None, 
                          user_role: str = "patient", skip: int = 0, limit: int = 20) -> Dict[str, Any]:
    """Get monitoring history from records table"""
    
@staticmethod
def share_monitoring_with_doctor(db, record_id: int, doctor_id: int, patient_id: int) -> Dict[str, Any]:
    """Share monitoring record with doctor"""
    
@staticmethod
def get_doctor_assigned_patients(db, doctor_id: int) -> List[Dict[str, Any]]:
    """Get patients assigned to doctor for monitoring selection"""
```

#### C. New Endpoints (`app/api/v1/endpoints/fetal_monitoring.py`):
```python
# BARU - Simplified endpoints

@router.post("/monitoring/process", response_model=ESP32MonitoringResponse)
async def process_monitoring_data(
    request: ESP32MonitoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process ESP32 monitoring data for both doctor and patient"""

@router.get("/monitoring/history", response_model=MonitoringHistoryResponse)  
async def get_monitoring_history(
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monitoring history (role-based access)"""
    
@router.post("/monitoring/share")
async def share_monitoring(
    request: ShareMonitoringRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Share monitoring record with doctor (patient only)"""

@router.get("/doctors/{doctor_id}/assigned-patients")
async def get_assigned_patients(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patients assigned to doctor for monitoring"""
```

---

## 📱 FASE 3: FRONTEND UPDATES

### A. Remove Old Features:
```dart
// HAPUS files/features:
- Pregnancy info management
- Complex session management
- Old monitoring flow screens
- Complex sharing mechanisms
```

### B. New Frontend Flow:

#### 🏥 **Doctor Monitoring Flow:**
```dart
// 1. Patient Selection Screen
class DoctorPatientSelectionScreen {
  // Load assigned patients from: GET /doctors/{doctor_id}/assigned-patients
  // Show list of patients for selection
}

// 2. ESP32 Connection Screen  
class ESP32ConnectionScreen {
  // Connect to ESP32 via Bluetooth/WiFi
  // Show connection status
}

// 3. Monitoring Screen
class MonitoringScreen {
  // Start/Stop monitoring buttons
  // Real-time BPM display from ESP32
  // Duration timer
}

// 4. Results Screen
class MonitoringResultsScreen {
  // Show classification results from backend
  // Notes input field
  // Save button
}

// 5. History Screen
class MonitoringHistoryScreen {
  // Load from: GET /monitoring/history
  // Show past monitoring records
}
```

#### 👤 **Patient Monitoring Flow:**
```dart
// 1. ESP32 Connection Screen (same as doctor)
// 2. Monitoring Screen (same as doctor)  
// 3. Results Screen (same as doctor + share option)
// 4. History Screen (same as doctor + share buttons)

class PatientHistoryScreen extends MonitoringHistoryScreen {
  // Additional: Share with doctor functionality
  // POST /monitoring/share
}
```

### C. New API Integration:
```dart
// ESP32 data processing
Future<MonitoringResult> processMonitoringData({
  required int patientId,
  required int gestationalAge, 
  required List<int> bpmReadings,
  String? notes,
}) async {
  // POST /api/v1/fetal-monitoring/monitoring/process
}

// Get monitoring history
Future<List<MonitoringRecord>> getMonitoringHistory({
  int? patientId,
  int skip = 0,
  int limit = 20,
}) async {
  // GET /api/v1/fetal-monitoring/monitoring/history
}

// Share with doctor
Future<void> shareMonitoringWithDoctor({
  required int recordId,
  required int doctorId,
  String? notes,
}) async {
  // POST /api/v1/fetal-monitoring/monitoring/share
}
```

---

## 🗃️ DATABASE CHANGES

### Records Table Usage:
```sql
-- Menggunakan existing records table dengan mapping:
-- id: auto increment
-- patient_id: patient yang dimonitor
-- created_by: doctor_id (untuk monitoring dokter) atau patient_user_id (untuk monitoring pasien)
-- start_time: waktu mulai monitoring
-- end_time: waktu selesai monitoring  
-- monitoring_duration: durasi dalam menit
-- heart_rate_data: JSON array of BPM readings dari ESP32
-- classification: hasil klasifikasi ("normal", "bradycardia", "tachycardia", "irregular")
-- notes: catatan pasien
-- doctor_notes: catatan dokter + sharing info
-- gestational_age: usia kehamilan
-- shared_with: doctor_id (untuk sharing)
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Backend:
- [ ] Remove old fetal monitoring endpoints
- [ ] Remove old service methods
- [ ] Remove old schemas
- [ ] Create new simplified schemas
- [ ] Create new service methods using records table
- [ ] Create new simplified endpoints
- [ ] Update doctor dashboard for patient selection
- [ ] Test all new endpoints

### Frontend:  
- [ ] Remove old monitoring screens
- [ ] Create new doctor patient selection screen
- [ ] Create new ESP32 connection screen
- [ ] Create new monitoring screen (start/stop)
- [ ] Create new results screen with classification
- [ ] Create new history screen
- [ ] Implement sharing functionality
- [ ] Update API service calls
- [ ] Test complete flow

### Testing:
- [ ] Test doctor monitoring flow end-to-end
- [ ] Test patient monitoring flow end-to-end  
- [ ] Test sharing functionality
- [ ] Test monitoring history
- [ ] Test ESP32 integration
- [ ] Test classification accuracy

---

**TARGET**: Simple, streamlined monitoring with ESP32 integration using only records table! 🎯
