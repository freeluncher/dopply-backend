# 🩺 PANDUAN TEKNIS ALUR MONITORING DOKTER - Dopply Fetal Monitoring

## 📋 DAFTAR ISI
1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Alur Monitoring Doctor](#alur-monitoring-doctor)
3. [Endpoint API & Integrasi Backend](#endpoint-api--integrasi-backend)
4. [Services & Data Flow](#services--data-flow)
5. [State Management](#state-management)
6. [Error Handling](#error-handling)
7. [Debugging Guide](#debugging-guide)
8. [Testing & Validation](#testing--validation)

---

## 🏗️ ARSITEKTUR SISTEM

### Struktur Komponen Doctor Monitoring

```
📁 Doctor Monitoring Architecture
├── 📂 Presentation Layer
│   ├── 🎯 Pages
│   │   ├── modern_fetal_monitoring_page.dart (Main monitoring UI)
│   │   ├── monitoring_page.dart (Legacy monitoring)
│   │   └── patient_monitoring_page.dart (Dashboard monitoring)
│   ├── 🧠 ViewModels/Notifiers
│   │   ├── fetal_monitoring_notifier.dart (Primary state management)
│   │   ├── monitoring_view_model.dart (Legacy view model)
│   │   └── monitoring_state.dart (State definitions)
│   └── 🎨 Widgets
│       ├── esp32_ble_bpm_stream_widget.dart (BLE connection)
│       ├── bpm_realtime_chart_widget.dart (Live charts)
│       └── monitoring_result_card.dart (Results display)
├── 📂 Data Layer
│   ├── 🔗 Services
│   │   ├── monitoring_api_service.dart (Doctor monitoring API)
│   │   ├── fetal_monitoring_api_service.dart (Fetal specific API)
│   │   └── medical_records_api_service.dart (Records management)
│   └── 📄 Models
│       ├── monitoring_patient.dart (Patient data models)
│       ├── fetal_monitoring.dart (Monitoring session models)
│       └── monitoring.dart (Core monitoring entities)
└── 🔧 Infrastructure
    ├── BLE Integration (ESP32 communication)
    ├── Token Authentication
    └── Real-time Data Streaming
```

---

## 🔄 ALUR MONITORING DOCTOR

### 1. **PERSIAPAN & AUTENTIKASI**

```dart
// 🔐 Step 1: Authentication & Token Validation
final tokenService = TokenStorageService();
final token = await tokenService.getToken();

// Validate token before proceeding
final isValid = await tokenService.isTokenValid();
if (!isValid) {
    // Auto-refresh token if needed
    final authService = AuthTokenService();
    await authService.refreshToken();
}
```

**Endpoint:**
- `GET /token/verify` - Verify token validity
- `POST /refresh` - Refresh expired token

### 2. **PEMILIHAN PASIEN**

```dart
// 👤 Step 2: Load and Select Patient
final monitoringApiService = MonitoringApiService();
final patients = await monitoringApiService.getPatientsByDoctorIdWithStorage(
    doctorId: doctorId,
    search: searchQuery,
);

// Select patient for monitoring
void selectPatient(MonitoringPatient patient) {
    state = state.copyWith(
        selectedPatient: patient,
        selectedPatientId: patient.id,
    );
}
```

**Endpoint:**
- `GET /doctors/{doctor_id}/patients` - Get doctor's patient list
- `GET /patients/{patient_id}` - Get specific patient details

### 3. **KONEKSI HARDWARE (ESP32/BLE)**

```dart
// 📡 Step 3: Establish BLE Connection
final bleService = ref.read(fetalDopplerBLEProvider.notifier);

// Connect to ESP32 device
await bleService.connectToDevice();

// Listen to BPM stream
_heartRateSubscription = bleService.heartRateStream.listen(
    (data) {
        if (state.isMonitoring) {
            // Add BPM reading to monitoring data
            addBpmReading(data.bpm);
        }
    },
    onError: (error) {
        state = state.copyWith(
            errorMessage: 'BLE Error: ${error.toString()}',
        );
    },
);
```

**Hardware Integration:**
- ESP32 BLE communication
- Real-time BPM data streaming
- Signal quality monitoring

### 4. **MEMULAI MONITORING SESSION**

```dart
// ▶️ Step 4: Start Monitoring Session
Future<void> startMonitoring({
    MonitoringType type = MonitoringType.clinic,
}) async {
    try {
        // Initialize monitoring state
        state = state.copyWith(
            isMonitoring: true,
            bpmData: [],
            startTime: DateTime.now(),
            monitoringType: type,
        );

        // Start BLE monitoring
        final bleService = ref.read(fetalDopplerBLEProvider.notifier);
        await bleService.startMonitoring();

        print('[MONITORING] Session started for patient: ${state.selectedPatient?.name}');
    } catch (e) {
        state = state.copyWith(
            errorMessage: 'Failed to start monitoring: ${e.toString()}',
            isMonitoring: false,
        );
    }
}
```

### 5. **PENGUMPULAN DATA BPM REAL-TIME**

```dart
// 📊 Step 5: Real-time BPM Data Collection
void addBpmReading(int bpm) {
    if (!state.isMonitoring) return;

    final updatedBpmData = [...state.bpmData, bpm];
    
    state = state.copyWith(
        bpmData: updatedBpmData,
        currentBpm: bpm,
        hasUnsavedData: true,
    );

    // Real-time classification (optional)
    if (updatedBpmData.length >= 10) {
        _performRealtimeClassification(updatedBpmData);
    }
}
```

### 6. **MENGHENTIKAN MONITORING**

```dart
// ⏹️ Step 6: Stop Monitoring Session
Future<void> stopMonitoring() async {
    try {
        // Stop BLE service
        final bleService = ref.read(fetalDopplerBLEProvider.notifier);
        await bleService.stopMonitoring();

        // Update state
        state = state.copyWith(
            isMonitoring: false,
            endTime: DateTime.now(),
        );

        print('[MONITORING] Session stopped. BPM data points: ${state.bpmData.length}');
    } catch (e) {
        state = state.copyWith(
            errorMessage: 'Failed to stop monitoring: ${e.toString()}',
            isMonitoring: false,
        );
    }
}
```

### 7. **KLASIFIKASI & ANALISIS DATA**

```dart
// 🧠 Step 7: Classify BPM Data
Future<void> _classifySession() async {
    try {
        if (state.bpmData.isEmpty) return;

        // Prepare data for classification
        final averageBpm = state.bpmData.isNotEmpty 
            ? (state.bpmData.reduce((a, b) => a + b) / state.bpmData.length).round()
            : 120;

        // Call classification API
        final result = await _apiService.classifyFetalBPM(
            bpm: averageBpm,
            gestationalAge: state.gestationalAge,
            readings: _convertToReadings(state.bpmData),
            token: token,
        );

        state = state.copyWith(
            classificationResult: result,
            averageBpm: averageBpm.toDouble(),
        );

    } catch (e) {
        print('[CLASSIFICATION] Error: ${e.toString()}');
        state = state.copyWith(
            errorMessage: 'Classification failed: ${e.toString()}',
        );
    }
}
```

**Endpoint:**
- `POST /fetal/classify` - Classify BPM data
- `POST /classify_bpm` - Alternative classification endpoint

### 8. **MENYIMPAN HASIL MONITORING**

```dart
// 💾 Step 8: Save Monitoring Session
Future<bool> saveMonitoringSession({String? doctorNotes}) async {
    try {
        // Get current doctor info
        final user = ref.read(userProvider);
        final doctorId = int.tryParse(user?.doctorId ?? user?.id ?? '0') ?? 0;

        // Create monitoring session
        final session = FetalMonitoringSession(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            patientId: int.tryParse(state.selectedPatientId!) ?? 0,
            doctorId: doctorId,
            type: state.monitoringType,
            gestationalAge: state.gestationalAge,
            startTime: state.startTime ?? DateTime.now(),
            endTime: state.endTime ?? DateTime.now(),
            readings: _convertToReadings(state.bpmData),
            doctorNotes: doctorNotes,
            result: state.classificationResult,
            isSharedWithDoctor: true,
        );

        // Save to backend
        await _apiService.saveMonitoringSession(
            session: session, 
            token: token
        );

        return true;
    } catch (e) {
        state = state.copyWith(
            errorMessage: 'Failed to save session: ${e.toString()}',
        );
        return false;
    }
}
```

**Endpoint:**
- `POST /fetal/sessions` - Save monitoring session
- `POST /monitoring_record` - Alternative save endpoint

---

## 🔗 ENDPOINT API & INTEGRASI BACKEND

### **Authentication Endpoints**

| Method | Endpoint | Purpose | Request Body |
|--------|----------|---------|--------------|
| `POST` | `/login` | Doctor login | `{email, password}` |
| `POST` | `/refresh` | Refresh token | `{refresh_token}` |
| `GET` | `/token/verify` | Verify token | Headers: `Bearer token` |

### **Patient Management Endpoints**

| Method | Endpoint | Purpose | Request Body |
|--------|----------|---------|--------------|
| `GET` | `/doctors/{doctor_id}/patients` | Get doctor's patients | Query: `?search=name` |
| `GET` | `/patients/{patient_id}` | Get patient details | - |
| `GET` | `/patients/{patient_id}/monitoring/history` | Patient monitoring history | Query: `?limit=10&offset=0` |

### **Monitoring Core Endpoints**

| Method | Endpoint | Purpose | Request Body |
|--------|----------|---------|--------------|
| `POST` | `/fetal/sessions` | Save monitoring session | `FetalMonitoringSession` object |
| `POST` | `/fetal/classify` | Classify BPM data | `{fhr_data, gestational_age, maternal_age}` |
| `GET` | `/fetal/sessions` | Get monitoring sessions | Query: `?patient_id=123&doctor_id=456` |
| `POST` | `/fetal/sessions/{id}/share` | Share session with doctor | `{doctor_id, notes}` |

### **Legacy Monitoring Endpoints**

| Method | Endpoint | Purpose | Request Body |
|--------|----------|---------|--------------|
| `POST` | `/monitoring` | Send monitoring result | `{patient_id, bpm_data, doctor_note}` |
| `POST` | `/classify_bpm` | Classify BPM data | `{bpm_data}` |
| `POST` | `/monitoring_record` | Save monitoring record | `{patient_id, bpm_data, notes}` |
| `GET` | `/patient/monitoring/history` | Get patient history | - |

### **Data Sharing Endpoints**

| Method | Endpoint | Purpose | Request Body |
|--------|----------|---------|--------------|
| `POST` | `/patient/share_monitoring` | Share monitoring with doctor | `{monitoring_id, doctor_id}` |
| `GET` | `/doctor/list` | Get available doctors | - |

---

## 🔧 SERVICES & DATA FLOW

### **1. FetalMonitoringApiService** (Primary Service)

```dart
class FetalMonitoringApiService {
    static const String _baseUrl = 'https://dopply.my.id/api/v1';

    // Core monitoring operations
    Future<Map<String, dynamic>> saveMonitoringRecord();
    Future<FetalMonitoringResult> classifyFetalBPM();
    Future<FetalMonitoringSession> saveMonitoringSession();
    Future<List<FetalMonitoringSession>> getPatientMonitoringSessions();
    Future<List<FetalMonitoringSession>> getDoctorMonitoringSessions();
    Future<bool> shareSessionWithDoctor();
}
```

### **2. MonitoringApiService** (Doctor Service)

```dart
class MonitoringApiService {
    // Doctor-specific operations
    Future<Map<String, dynamic>?> sendMonitoringResult();
    Future<List<Map<String, dynamic>>> getPatientsByDoctorId();
    Future<Map<String, dynamic>?> classifyBpmData();
}
```

### **3. MedicalRecordsApiService** (Records Management)

```dart
class MedicalRecordsApiService {
    // Medical records operations
    Future<PatientMonitoringHistory> getPatientMonitoringHistory();
    Future<List<MedicalRecord>> getMonitoringHistory();
    Future<bool> shareMonitoringToDoctor();
}
```

### **Data Flow Diagram**

```
🔄 Doctor Monitoring Data Flow

[Doctor] → [UI Input] → [ViewModel/Notifier] → [API Service] → [Backend]
   ↓                                                              ↓
[Patient Selection] → [BLE Connection] → [Real-time BPM] → [Database]
   ↓                                                              ↓
[Start Monitoring] → [Data Collection] → [Classification] → [Storage]
   ↓                                                              ↓
[Stop Monitoring] → [Save Session] → [Share with Doctor] → [Records]
```

---

## 🧠 STATE MANAGEMENT

### **FetalMonitoringState (Primary State)**

```dart
class FetalMonitoringState {
    // Patient Selection
    final MonitoringPatient? selectedPatient;
    final String selectedPatientId;
    
    // Monitoring Session
    final bool isMonitoring;
    final DateTime? startTime;
    final DateTime? endTime;
    final MonitoringType monitoringType;
    
    // BPM Data
    final List<int> bpmData;
    final int currentBpm;
    final double? averageBpm;
    
    // Classification Results
    final FetalMonitoringResult? classificationResult;
    final String? riskLevel;
    
    // Metadata
    final int gestationalAge;
    final bool hasUnsavedData;
    final String? errorMessage;
    final bool isLoading;
}
```

### **State Management Providers**

```dart
// Primary monitoring provider
final fetalMonitoringProvider = StateNotifierProvider<FetalMonitoringNotifier, FetalMonitoringState>();

// Patient list provider
final patientsByDoctorProvider = FutureProvider<List<Map<String, dynamic>>>();

// BLE service provider
final fetalDopplerBLEProvider = StateNotifierProvider<FetalDopplerBLEService, BLEState>();
```

---

## ⚠️ ERROR HANDLING

### **Common Error Scenarios & Solutions**

#### **1. Authentication Errors**

```dart
// Token expired
if (response.statusCode == 401) {
    try {
        final authService = AuthTokenService();
        final refreshSuccess = await authService.refreshToken();
        
        if (refreshSuccess) {
            // Retry operation with new token
            return await retryOperation();
        } else {
            // Redirect to login
            throw Exception('Please login again');
        }
    } catch (e) {
        throw Exception('Authentication failed: $e');
    }
}
```

#### **2. Network Connectivity Issues**

```dart
// Handle network errors
try {
    final response = await apiCall();
} on SocketException {
    throw Exception('Network connection error. Please check your internet.');
} on TimeoutException {
    throw Exception('Request timeout. Please try again.');
} on HttpException catch (e) {
    if (e.message.contains('502')) {
        throw Exception('Server temporarily unavailable. Please try again later.');
    }
    rethrow;
}
```

#### **3. BLE Connection Issues**

```dart
// Handle BLE errors
_heartRateSubscription = bleService.heartRateStream.listen(
    (data) {
        // Process BPM data
        addBpmReading(data.bpm);
    },
    onError: (error) {
        if (error.toString().contains('device disconnected')) {
            state = state.copyWith(
                errorMessage: 'Device disconnected. Please reconnect ESP32.',
                isMonitoring: false,
            );
        } else {
            state = state.copyWith(
                errorMessage: 'BLE Error: ${error.toString()}',
            );
        }
    },
);
```

#### **4. Data Validation Errors**

```dart
// Validate monitoring data before saving
if (state.bpmData.isEmpty) {
    throw Exception('No BPM data available for saving');
}

if (state.selectedPatient == null) {
    throw Exception('No patient selected for monitoring');
}

if (state.gestationalAge < 20 || state.gestationalAge > 42) {
    throw Exception('Invalid gestational age. Must be between 20-42 weeks.');
}
```

---

## 🐛 DEBUGGING GUIDE

### **Step-by-Step Debugging Process**

#### **1. Verify Authentication**

```dart
// Debug authentication
final tokenService = TokenStorageService();
await tokenService.debugSessionInfo();

// Check token validity
final token = await tokenService.getToken();
print('Token: ${token?.substring(0, 20)}...');

final isValid = await tokenService.isTokenValid();
print('Token valid: $isValid');
```

#### **2. Test Patient Loading**

```dart
// Debug patient loading
try {
    final patients = await monitoringApiService.getPatientsByDoctorIdWithStorage(
        doctorId: doctorId,
    );
    print('Loaded ${patients.length} patients');
    
    for (final patient in patients) {
        print('Patient: ${patient['name']} (ID: ${patient['id']})');
    }
} catch (e) {
    print('Patient loading error: $e');
}
```

#### **3. Test BLE Connection**

```dart
// Debug BLE connection
final bleService = ref.read(fetalDopplerBLEProvider.notifier);

try {
    await bleService.connectToDevice();
    print('BLE connected successfully');
    
    // Test data stream
    _subscription = bleService.heartRateStream.listen(
        (data) => print('BPM received: ${data.bpm}'),
        onError: (error) => print('BLE error: $error'),
    );
} catch (e) {
    print('BLE connection failed: $e');
}
```

#### **4. Test API Classification**

```dart
// Debug classification API
try {
    final testBpmData = [120, 125, 130, 128, 122];
    
    final result = await fetalApiService.classifyFetalBPM(
        bpm: 125,
        gestationalAge: 32,
        readings: convertToReadings(testBpmData),
        token: token,
    );
    
    print('Classification result: ${result.overallClassification}');
    print('Risk level: ${result.riskLevel}');
} catch (e) {
    print('Classification error: $e');
}
```

#### **5. Test Session Saving**

```dart
// Debug session saving
try {
    final session = FetalMonitoringSession(
        id: 'test_${DateTime.now().millisecondsSinceEpoch}',
        patientId: patientId,
        doctorId: doctorId,
        type: MonitoringType.clinic,
        gestationalAge: 32,
        startTime: DateTime.now().subtract(Duration(minutes: 10)),
        endTime: DateTime.now(),
        readings: testReadings,
        doctorNotes: 'Test session',
        isSharedWithDoctor: true,
    );
    
    final savedSession = await fetalApiService.saveMonitoringSession(
        session: session,
        token: token,
    );
    
    print('Session saved with ID: ${savedSession.id}');
} catch (e) {
    print('Session save error: $e');
}
```

### **Debug Console Outputs**

```dart
// Enable debug logging
void enableDebugLogging() {
    print('[MONITORING] Debug mode enabled');
    
    // Log state changes
    ref.listen(fetalMonitoringProvider, (previous, next) {
        print('[STATE] Monitoring: ${next.isMonitoring}');
        print('[STATE] BPM Data points: ${next.bpmData.length}');
        print('[STATE] Selected patient: ${next.selectedPatient?.name}');
        
        if (next.errorMessage != null) {
            print('[ERROR] ${next.errorMessage}');
        }
    });
}
```

### **Common Debug Checkpoints**

| Checkpoint | What to Check | Expected Result |
|------------|---------------|-----------------|
| **Auth Token** | `await tokenService.getToken()` | Valid JWT token string |
| **Patient List** | `getPatientsByDoctorId()` | Array of patient objects |
| **BLE Status** | `bleService.isConnected` | `true` when ESP32 connected |
| **BPM Stream** | `heartRateStream.listen()` | Regular BPM integer values |
| **Classification** | `classifyFetalBPM()` | Valid classification result |
| **Session Save** | `saveMonitoringSession()` | Session ID returned |

---

## ✅ TESTING & VALIDATION

### **Unit Tests**

```dart
// Test monitoring state management
void main() {
    group('FetalMonitoringNotifier Tests', () {
        test('should start monitoring successfully', () async {
            final notifier = FetalMonitoringNotifier(ref);
            
            await notifier.startMonitoring();
            
            expect(notifier.state.isMonitoring, true);
            expect(notifier.state.bpmData, isEmpty);
        });
        
        test('should add BPM readings during monitoring', () {
            final notifier = FetalMonitoringNotifier(ref);
            notifier.state = notifier.state.copyWith(isMonitoring: true);
            
            notifier.addBpmReading(125);
            notifier.addBpmReading(130);
            
            expect(notifier.state.bpmData.length, 2);
            expect(notifier.state.bpmData, [125, 130]);
        });
    });
}
```

### **Integration Tests**

```dart
// Test API integration
void main() {
    group('API Integration Tests', () {
        test('should authenticate and load patients', () async {
            final token = await authenticateTestUser();
            final patients = await loadTestPatients(token);
            
            expect(patients, isNotEmpty);
            expect(patients.first, containsPair('name', isNotNull));
        });
        
        test('should save monitoring session', () async {
            final session = createTestSession();
            final result = await saveTestSession(session);
            
            expect(result.success, true);
            expect(result.sessionId, isNotNull);
        });
    });
}
```

### **Manual Testing Checklist**

- [ ] **Login dengan akun doctor**
- [ ] **Load daftar pasien doctor**
- [ ] **Pilih pasien untuk monitoring**
- [ ] **Connect ke ESP32 device**
- [ ] **Start monitoring session**
- [ ] **Terima BPM data real-time**
- [ ] **Stop monitoring session**
- [ ] **Klasifikasi data BPM**
- [ ] **Save session ke backend**
- [ ] **Verify data tersimpan di database**

---

## 🚀 IMPLEMENTASI BEST PRACTICES

### **1. Performance Optimization**

```dart
// Optimize BPM data collection
void addBpmReading(int bpm) {
    // Limit data points to prevent memory issues
    const maxDataPoints = 1000;
    
    final updatedData = [...state.bpmData];
    if (updatedData.length >= maxDataPoints) {
        updatedData.removeAt(0); // Remove oldest reading
    }
    updatedData.add(bpm);
    
    state = state.copyWith(bpmData: updatedData);
}
```

### **2. Error Recovery**

```dart
// Implement retry mechanism
Future<T> withRetry<T>(Future<T> Function() operation, {int maxRetries = 3}) async {
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await operation();
        } catch (e) {
            if (attempt == maxRetries) rethrow;
            
            // Exponential backoff
            await Future.delayed(Duration(seconds: attempt * 2));
        }
    }
    throw Exception('Max retries exceeded');
}
```

### **3. Data Consistency**

```dart
// Ensure data consistency
Future<void> validateAndSave() async {
    // Validate data before saving
    if (!_validateMonitoringData()) {
        throw Exception('Invalid monitoring data');
    }
    
    // Create backup before saving
    final backup = state.copyWith();
    
    try {
        await saveMonitoringSession();
    } catch (e) {
        // Restore from backup on failure
        state = backup;
        rethrow;
    }
}
```

---

## 📞 SUPPORT & TROUBLESHOOTING

### **Frequently Asked Questions**

**Q: Monitoring session tidak bisa dimulai?**
- Pastikan token authentication masih valid
- Cek koneksi ESP32/BLE device
- Verify pasien sudah dipilih dengan benar

**Q: BPM data tidak muncul?**
- Cek koneksi BLE ke ESP32
- Pastikan device ESP32 broadcasting data
- Verify `heartRateStream` subscription aktif

**Q: Error saat menyimpan session?**
- Cek koneksi internet
- Validate token authentication
- Pastikan data BPM tidak kosong
- Verify patient ID valid

**Q: Classification tidak akurat?**
- Pastikan minimal 10 data points BPM
- Cek gestational age dalam range valid (20-42 weeks)
- Verify backend classification service running

---

## 🎯 KESIMPULAN

Dokumentasi ini menyediakan panduan lengkap untuk:

1. ✅ **Memahami arsitektur sistem monitoring doctor**
2. ✅ **Mengintegrasikan dengan backend API**
3. ✅ **Mengelola state management yang efisien**
4. ✅ **Melakukan debugging dan troubleshooting**
5. ✅ **Mengimplementasikan best practices**

Dengan mengikuti panduan ini, Anda dapat:
- Mengidentifikasi dan memperbaiki bug dengan cepat
- Memastikan integrasi backend berjalan lancar
- Mengoptimalkan performance aplikasi
- Memberikan user experience yang baik untuk dokter

**Tim Development:** Gunakan panduan ini sebagai referensi utama untuk debugging dan pengembangan fitur monitoring doctor selanjutnya.

---

## 🚨 **BACKEND FIXED - FRONTEND UPDATE REQUIRED**

### **ISSUE RESOLVED:**
Backend endpoint `GET /api/v1/doctors/{doctor_id}/patients` telah diperbaiki dan sekarang berfungsi dengan baik.

### **TEST RESULTS:**
- ✅ Endpoint responds correctly (401 for unauthorized, not 404)
- ✅ Authentication system working  
- ✅ Query parameters supported (`limit`, `offset`, `search`, `status`)
- ✅ Response format sesuai dengan expected frontend format

---

## 📱 **PROMPT UNTUK FRONTEND DEVELOPER**

### **🎯 URGENT ACTION REQUIRED: Update Doctor Monitoring App**

Backend API untuk doctor patients endpoint telah diperbaiki. Silakan lakukan update berikut pada aplikasi Flutter:

### **1. IMMEDIATE FIXES NEEDED:**

#### **A. Update API Service Error Handling**
```dart
// File: monitoring_api_service.dart
// Lokasi: lib/services/monitoring_api_service.dart

Future<List<Map<String, dynamic>>> getPatientsByDoctorIdWithStorage({
    required int doctorId,
    String? search,
    int limit = 50,
    int offset = 0,
}) async {
    try {
        print('[API] Loading patients for doctor: $doctorId');
        
        // Build query parameters
        final queryParams = <String, dynamic>{
            'limit': limit,
            'offset': offset,
        };
        
        if (search != null && search.isNotEmpty) {
            queryParams['search'] = search;
        }
        
        // Primary endpoint (now working)
        final response = await dio.get(
            '/doctors/$doctorId/patients',
            queryParameters: queryParams,
        );
        
        print('[API] ✅ Successfully loaded ${response.data['patients']?.length ?? 0} patients');
        
        // Return patients array from response
        final patients = List<Map<String, dynamic>>.from(
            response.data['patients'] ?? []
        );
        
        return patients;
        
    } catch (e) {
        print('[API] ❌ Error loading patients: $e');
        
        // Enhanced error handling
        if (e.response?.statusCode == 401) {
            throw Exception('Authentication required. Please login again.');
        } else if (e.response?.statusCode == 403) {
            throw Exception('Access denied. Doctor can only view their own patients.');
        } else if (e.response?.statusCode == 404) {
            throw Exception('Doctor not found or has no assigned patients.');
        } else {
            throw Exception('Failed to load patients: ${e.toString()}');
        }
    }
}
```

#### **B. Update Patient Loading Logic in Notifier**
```dart
// File: fetal_monitoring_notifier.dart
// Lokasi: lib/providers/fetal_monitoring_notifier.dart

Future<void> loadDoctorPatients() async {
    try {
        state = state.copyWith(isLoading: true, errorMessage: null);
        
        // Get doctor ID from current user
        final user = ref.read(userProvider);
        final doctorId = int.tryParse(user?.doctorId ?? user?.id ?? '0');
        
        if (doctorId == null || doctorId == 0) {
            throw Exception('Invalid doctor ID. Please login again.');
        }
        
        print('[NOTIFIER] Loading patients for doctor ID: $doctorId');
        
        // Load patients from API
        final patients = await _monitoringApiService.getPatientsByDoctorIdWithStorage(
            doctorId: doctorId,
            search: state.searchQuery,
            limit: 50,
            offset: 0,
        );
        
        print('[NOTIFIER] ✅ Loaded ${patients.length} patients');
        
        // Convert to MonitoringPatient objects
        final patientList = patients.map((patientData) {
            return MonitoringPatient(
                id: patientData['id']?.toString() ?? '',
                name: patientData['name'] ?? '',
                email: patientData['email'] ?? '',
                birthDate: patientData['birth_date'],
                address: patientData['address'],
                medicalNote: patientData['medical_note'],
                assignmentDate: patientData['assignment_date'],
                status: patientData['status'],
                doctorNotes: patientData['doctor_notes'],
            );
        }).toList();
        
        state = state.copyWith(
            patients: patientList,
            isLoading: false,
            errorMessage: null,
        );
        
    } catch (e) {
        print('[NOTIFIER] ❌ Error loading patients: $e');
        
        state = state.copyWith(
            patients: [],
            isLoading: false,
            errorMessage: e.toString(),
        );
    }
}
```

#### **C. Update Patient Model (if needed)**
```dart
// File: monitoring_patient.dart
// Ensure model supports new fields from backend

class MonitoringPatient {
    final String id;
    final String name;
    final String email;
    final DateTime? birthDate;
    final String? address;
    final String? medicalNote;
    final DateTime? assignmentDate;  // NEW FIELD
    final String? status;           // NEW FIELD  
    final String? doctorNotes;      // NEW FIELD
    
    MonitoringPatient({
        required this.id,
        required this.name,
        required this.email,
        this.birthDate,
        this.address,
        this.medicalNote,
        this.assignmentDate,  // ADD THIS
        this.status,          // ADD THIS
        this.doctorNotes,     // ADD THIS
    });
    
    factory MonitoringPatient.fromJson(Map<String, dynamic> json) {
        return MonitoringPatient(
            id: json['id']?.toString() ?? '',
            name: json['name'] ?? '',
            email: json['email'] ?? '',
            birthDate: json['birth_date'] != null 
                ? DateTime.tryParse(json['birth_date']) 
                : null,
            address: json['address'],
            medicalNote: json['medical_note'],
            assignmentDate: json['assignment_date'] != null
                ? DateTime.tryParse(json['assignment_date'])
                : null,
            status: json['status'],
            doctorNotes: json['doctor_notes'],
        );
    }
}
```

### **2. TESTING CHECKLIST:**
