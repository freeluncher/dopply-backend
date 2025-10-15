# 🚀 **FRONTEND INTEGRATION GUIDE - DOPPLY BACKEND API**

## 📋 **OVERVIEW**

Backend Dopply telah dikonsolidasi dan dioptimalkan dengan **32 endpoint** yang tersedia untuk integrasi frontend. Semua endpoint menggunakan **FastAPI** dengan **JSON response format** yang konsisten.

**Base URL**: `https://dopply.my.id/api/v1`  
**Authentication**: Bearer Token (JWT)

---

## 🔑 **AUTHENTICATION ENDPOINTS**

### **1. Login User**
```http
POST /auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "token": "jwt_access_token",
    "refreshToken": "jwt_refresh_token",
    "user": {
      "id": 1,
      "userId": 1,
      "name": "John Doe",
      "email": "user@example.com",
      "role": "patient|doctor|admin",
      "profilePhotoUrl": "https://dopply.my.id/static/photos/user.jpg",
      // Patient-specific fields (if role = "patient")
      "hpht": "2024-01-01",
      "birthDate": "1990-01-01",
      "address": "Jakarta",
      "medicalNote": "No allergies"
    }
  },
  "message": "Login successful"
}
```

### **2. Refresh Token**
```http
POST /refresh
```

**Headers**: `Authorization: Bearer <refresh_token>`

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "new_jwt_token",
    "token_type": "bearer"
  }
}
```

### **3. Token Verification**
```http
GET /token/verify
```

**Headers**: `Authorization: Bearer <access_token>`

### **4. User Registration**
```http
POST /user/register
```

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "patient|doctor",
  "specialization": "Obstetrics" // Required for doctors only
}
```

### **5. Logout**
```http
POST /auth/logout  
```

---

## 👨‍⚕️ **USER MANAGEMENT ENDPOINTS**

### **6. Get All Doctors**
```http
GET /user/all-doctors
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "userId": 2,
      "name": "Dr. Jane Smith",
      "email": "jane@example.com",
      "specialization": "Obstetrics",
      "profilePhotoUrl": "https://dopply.my.id/static/photos/doctor2.jpg"
    }
  ]
}
```

### **7. Upload Patient Profile Photo**
```http
POST /user/patient/profile/photo
```

**Content-Type**: `multipart/form-data`  
**Body**: `photo` (file)

### **8. Upload Doctor Profile Photo**
```http
POST /user/doctor/profile/photo
```

**Content-Type**: `multipart/form-data`  
**Body**: `photo` (file)

### **9. Update Doctor Profile**
```http
PUT /user/doctor/profile
```

**Request Body**:
```json
{
  "name": "Dr. Jane Smith",
  "email": "jane@example.com", 
  "specialization": "Obstetrics"
}
```

### **10. Get Doctor Profile**
```http
GET /user/doctor/profile
```

---

## 🏥 **PATIENT MANAGEMENT ENDPOINTS**

### **11. Get Patient Details**
```http
GET /patient/{patient_id}
```

### **12. Update Patient Details**  
```http
PUT /patient/{patient_id}
```

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "hpht": "2024-01-01",
  "birthDate": "1990-01-01", 
  "address": "Jakarta",
  "medicalNote": "No known allergies"
}
```

### **13. Upload Patient Profile Photo**
```http
POST /patient/{patient_id}/profile-photo
```

### **14. Get Patient (Legacy)**
```http
GET /patient/legacy/{id}
```

### **15. Update Patient (Legacy)**
```http
PUT /patient/legacy/{id}
```

---

## 👨‍⚕️ **DOCTOR MANAGEMENT ENDPOINTS**

### **16. Get Doctor Details**
```http
GET /doctor/{doctor_id}
```

### **17. Update Doctor Details**
```http
PUT /doctor/{doctor_id}
```

### **18. Upload Doctor Profile Photo**
```http
POST /doctor/{doctor_id}/profile-photo
```

---

## 📊 **MONITORING ENDPOINTS**

### **19. Classify BPM (Real-time)**
```http
POST /monitoring/classify
```

**Request Body**:
```json
{
  "bpm_data": [120, 125, 130, 128],
  "gestational_age": 32
}
```

**Response**:
```json
{
  "classification": "normal|bradikardia|takikardia",
  "average_bpm": 125.75
}
```

### **20. Submit Monitoring (Legacy)**
```http
POST /monitoring/submit
```

**Request Body**:
```json
{
  "patient_id": 1,
  "gestational_age": 32,
  "bpm_data": [120, 125, 130, 128],
  "start_time": "2024-10-15T10:00:00Z",
  "end_time": "2024-10-15T10:10:00Z",
  "notes": "Patient feeling well",
  "doctor_notes": "Normal monitoring session"
}
```

### **21. Save Monitoring Results**
```http
POST /monitoring/results
```

**Request Body**:
```json
{
  "patientId": 1,
  "avgBpm": 125,
  "minBpm": 110,
  "maxBpm": 140,
  "duration": 600,
  "dataPoints": [120, 125, 130, 128, 135],
  "timestamp": "2024-10-15T10:00:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "patientId": 1,
    "avgBpm": 125,
    "minBpm": 110,
    "maxBpm": 140,
    "duration": 600,
    "classification": "normal",
    "sharedWithDoctor": false,
    "timestamp": "2024-10-15T10:00:00Z",
    "createdAt": "2024-10-15T10:00:00Z"
  },
  "message": "Monitoring result saved successfully"
}
```

### **22. Get Monitoring History**
```http
GET /monitoring/history?patient_id=1&skip=0&limit=20
```

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 123,
        "patientId": 1,
        "patientName": "John Doe",
        "avgBpm": 125,
        "minBpm": 110,
        "maxBpm": 140,
        "duration": 600,
        "classification": "normal",
        "sharedWithDoctor": false,
        "timestamp": "2024-10-15T10:00:00Z"
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

### **23. Get Doctor Monitoring History**
```http
GET /monitoring/doctor-history?skip=0&limit=20
```

### **24. Share Monitoring with Doctor**
```http
POST /monitoring/share
```

**Request Body**:
```json
{
  "record_id": 123,
  "doctor_id": 2,
  "notes": "Please review this monitoring session"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Monitoring result shared with Dr. Jane Smith",
  "notification_id": 456
}
```

### **25. Get Doctor's Patients**
```http
GET /monitoring/patients
```

**Response**:
```json
{
  "patients": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "hpht": "2024-01-01",
      "gestational_age_weeks": 32,
      "last_monitoring": "2024-10-15T10:00:00Z"
    }
  ],
  "total_count": 10
}
```

### **26. Add Patient to Doctor**
```http
POST /monitoring/patients/add
```

**Request Body**:
```json
{
  "patient_email": "patient@example.com",
  "notes": "New patient assignment"
}
```

### **27. Get Notifications**
```http
GET /monitoring/notifications
```

**Response**:
```json
{
  "notifications": [
    {
      "id": 456,
      "from_patient_name": "John Doe",
      "record_id": 123,
      "message": "Monitoring result shared by John Doe",
      "created_at": "2024-10-15T10:00:00Z",
      "is_read": false
    }
  ],
  "unread_count": 5
}
```

### **28. Mark Notification as Read**
```http
POST /monitoring/notifications/read/{notification_id}
```

---

## 👑 **ADMIN ENDPOINTS**

### **29. Verify Doctor (Admin Only)**
```http
POST /monitoring/admin/verify-doctor
```

**Request Body**:
```json
{
  "doctor_id": 2,
  "is_verified": true
}
```

### **30. Get Doctor Validation Requests Count**
```http
GET /admin/doctor/validation-requests/count
```

### **31. Get Doctor Validation Requests**
```http
GET /admin/doctor/validation-requests
```

### **32. Validate Doctor**
```http
POST /admin/doctor/validate/{doctor_id}
```

---

## 🔐 **AUTHENTICATION & AUTHORIZATION**

### **Headers Required**:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### **User Roles & Permissions**:

| **Role** | **Endpoints Access** |
|----------|---------------------|
| **Patient** | Auth, Patient Management, Monitoring (own data), Share |
| **Doctor** | Auth, Doctor Management, Patient Management, Monitoring (assigned patients), Notifications |
| **Admin** | All endpoints + Admin validation |

---

## 📱 **FRONTEND IMPLEMENTATION EXAMPLES**

### **Flutter/Dart Example**:
```dart
class ApiService {
  static const String baseUrl = 'https://dopply.my.id/api/v1';
  
  // Login
  Future<LoginResponse> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );
    return LoginResponse.fromJson(jsonDecode(response.body));
  }
  
  // Save Monitoring
  Future<MonitoringResponse> saveMonitoring(MonitoringData data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/monitoring/results'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${await getToken()}',
      },
      body: jsonEncode({
        'patientId': data.patientId,
        'avgBpm': data.avgBpm,
        'minBpm': data.minBpm,
        'maxBpm': data.maxBpm,
        'duration': data.duration,
        'dataPoints': data.dataPoints,
        'timestamp': data.timestamp.toIso8601String(),
      }),
    );
    return MonitoringResponse.fromJson(jsonDecode(response.body));
  }
}
```

### **JavaScript/React Example**:
```javascript
const API_BASE = 'https://dopply.my.id/api/v1';

// API Client
class ApiClient {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.headers,
      },
      ...options,
    });
    return response.json();
  }
  
  // Login
  async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }
  
  // Get Monitoring History
  async getMonitoringHistory(patientId, skip = 0, limit = 20) {
    return this.request(
      `/monitoring/history?patient_id=${patientId}&skip=${skip}&limit=${limit}`
    );
  }
}
```

---

## 🚨 **ERROR HANDLING**

### **Standard Error Response**:
```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

### **Common HTTP Status Codes**:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error)
- **401**: Unauthorized (invalid/expired token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **422**: Unprocessable Entity (validation error)
- **500**: Internal Server Error

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Authentication Flow**:
- [ ] Implement login with email/password
- [ ] Store JWT tokens securely
- [ ] Implement token refresh logic
- [ ] Handle token expiration
- [ ] Implement logout functionality

### **User Management**:
- [ ] User registration (patient/doctor)
- [ ] Profile management (view/edit)
- [ ] Photo upload functionality
- [ ] Role-based UI components

### **Monitoring Features**:
- [ ] Real-time BPM classification
- [ ] Monitoring data collection & storage
- [ ] Monitoring history display
- [ ] Share monitoring with doctors
- [ ] Notifications system

### **Doctor Features**:
- [ ] Patient assignment management
- [ ] Doctor-patient monitoring history
- [ ] Notification management
- [ ] Patient list management

### **Admin Features**:
- [ ] Doctor verification system
- [ ] Validation requests management
- [ ] Admin dashboard

---

## 🔄 **DATA MODELS**

### **User Model**:
```typescript
interface User {
  id: number;
  userId: number;
  name: string;
  email: string;
  role: 'patient' | 'doctor' | 'admin';
  profilePhotoUrl?: string;
  // Patient specific
  hpht?: string;
  birthDate?: string;
  address?: string;
  medicalNote?: string;
  // Doctor specific  
  specialization?: string;
}
```

### **Monitoring Model**:
```typescript
interface MonitoringRecord {
  id: number;
  patientId: number;
  patientName?: string;
  avgBpm: number;
  minBpm: number;
  maxBpm: number;
  duration: number;
  classification: 'normal' | 'bradikardia' | 'takikardia';
  sharedWithDoctor: boolean;
  timestamp: string;
  createdAt: string;
}
```

### **Notification Model**:
```typescript
interface Notification {
  id: number;
  from_patient_name: string;
  record_id: number;
  message: string;
  created_at: string;
  is_read: boolean;
}
```

---

## ✅ **READY FOR INTEGRATION**

Semua endpoint telah dikonsolidasi dan dioptimalkan. Backend siap untuk integrasi frontend dengan:
- **32 endpoint** lengkap dan teruji
- **Konsistensi response format**
- **Proper authentication & authorization**
- **Role-based access control**
- **Error handling yang komprehensif**

**Start integrating now!** 🚀