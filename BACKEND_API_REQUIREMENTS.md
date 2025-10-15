# Backend API Requirements untuk Aplikasi Dopply

## Overview
Dokumen ini berisi spesifikasi lengkap endpoint API yang dibutuhkan oleh aplikasi Flutter Dopply untuk fitur profile management dan monitoring pasien.

**Base URL:** `https://dopply.my.id/api/v1`

**Authentication:** Semua endpoint memerlukan Bearer token di header:
```
Authorization: Bearer {token}
```

---

## 1. Authentication Endpoints

### 1.1 Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "refresh_token_here",
    "user": {
      "id": 1,
      "userId": 123,
      "name": "Dr. John Doe",
      "email": "john@example.com",
      "role": "doctor",
      "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/photo.jpg"
    }
  },
  "message": "Login successful"
}
```

**Response untuk Pasien:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "refresh_token_here",
    "user": {
      "id": 1,
      "userId": 456,
      "name": "Jane Doe",
      "email": "jane@example.com",
      "role": "patient",
      "hpht": "2024-01-15",
      "birthDate": "1995-06-20",
      "address": "Jl. Contoh No. 123",
      "medicalNote": "Riwayat diabetes",
      "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/jane.jpg"
    }
  },
  "message": "Login successful"
}
```

---

## 2. Patient Endpoints

### 2.1 Get Patient by ID
**Endpoint:** `GET /patients/:id`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 456,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "hpht": "2024-01-15",
    "birthDate": "1995-06-20",
    "address": "Jl. Contoh No. 123, Jakarta",
    "medicalNote": "Riwayat diabetes, alergi penisilin",
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/jane.jpg",
    "createdAt": "2024-01-01T10:00:00.000Z",
    "updatedAt": "2024-01-15T14:30:00.000Z"
  },
  "message": "Patient data retrieved successfully"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Patient not found"
}
```

### 2.2 Update Patient Data
**Endpoint:** `PUT /patients/:id`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Jane Doe Updated",
  "email": "jane.updated@example.com",
  "hpht": "2024-01-20",
  "birthDate": "1995-06-20",
  "address": "Jl. Baru No. 456, Jakarta Selatan",
  "medicalNote": "Riwayat diabetes, alergi penisilin, hipertensi"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 456,
    "name": "Jane Doe Updated",
    "email": "jane.updated@example.com",
    "hpht": "2024-01-20",
    "birthDate": "1995-06-20",
    "address": "Jl. Baru No. 456, Jakarta Selatan",
    "medicalNote": "Riwayat diabetes, alergi penisilin, hipertensi",
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/jane.jpg",
    "updatedAt": "2024-01-15T15:00:00.000Z"
  },
  "message": "Patient data updated successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "email": "Invalid email format",
    "hpht": "Invalid date format"
  }
}
```

### 2.3 Upload Patient Profile Photo
**Endpoint:** `POST /patients/:id/profile-photo`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```
photo: [File] (image file - jpg, jpeg, png)
```

**Important Notes:**
- Field name MUST be `photo`
- Accepted formats: jpg, jpeg, png
- Maximum file size: 5MB (recommended)
- Image will be automatically resized/optimized on server

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/patient_456_1234567890.jpg"
  },
  "message": "Profile photo uploaded successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Invalid file format. Only jpg, jpeg, png allowed"
}
```

**Response (413 Payload Too Large):**
```json
{
  "success": false,
  "message": "File size exceeds maximum limit of 5MB"
}
```

---

## 3. Doctor Endpoints

### 3.1 Get Doctor by ID
**Endpoint:** `GET /doctors/:id`

**Headers:**
```
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 123,
    "name": "Dr. John Doe",
    "email": "john@example.com",
    "specialization": "Obstetri dan Ginekologi",
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/doctor_123.jpg",
    "createdAt": "2024-01-01T10:00:00.000Z",
    "updatedAt": "2024-01-15T14:30:00.000Z"
  },
  "message": "Doctor data retrieved successfully"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Doctor not found"
}
```

### 3.2 Update Doctor Data
**Endpoint:** `PUT /doctors/:id`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Dr. John Doe Updated",
  "email": "john.updated@example.com",
  "specialization": "Obstetri, Ginekologi, dan Fetomaternal"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 123,
    "name": "Dr. John Doe Updated",
    "email": "john.updated@example.com",
    "specialization": "Obstetri, Ginekologi, dan Fetomaternal",
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/doctor_123.jpg",
    "updatedAt": "2024-01-15T15:30:00.000Z"
  },
  "message": "Doctor data updated successfully"
}
```

### 3.3 Upload Doctor Profile Photo
**Endpoint:** `POST /doctors/:id/profile-photo`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Request Body (multipart/form-data):**
```
photo: [File] (image file - jpg, jpeg, png)
```

**Important Notes:**
- Field name MUST be `photo`
- Accepted formats: jpg, jpeg, png
- Maximum file size: 5MB (recommended)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "profilePhotoUrl": "https://dopply.my.id/uploads/profiles/doctor_123_1234567890.jpg"
  },
  "message": "Profile photo uploaded successfully"
}
```

---

## 4. Monitoring Endpoints

### 4.1 Save Monitoring Result
**Endpoint:** `POST /monitoring/results`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "patientId": 1,
  "avgBpm": 142,
  "minBpm": 125,
  "maxBpm": 160,
  "duration": 300,
  "dataPoints": [120, 125, 130, 135, 140, 145, 150, 155, 160, 155, 150],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "patientId": 1,
    "avgBpm": 142,
    "minBpm": 125,
    "maxBpm": 160,
    "duration": 300,
    "classification": "Normal",
    "sharedWithDoctor": false,
    "timestamp": "2024-01-15T10:30:00.000Z",
    "createdAt": "2024-01-15T10:30:05.000Z"
  },
  "message": "Monitoring result saved successfully"
}
```

### 4.2 Get Monitoring History (for Patient)
**Endpoint:** `GET /monitoring/history`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
```
?patientId=1&limit=20&offset=0&sortBy=timestamp&order=desc
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 123,
        "patientId": 1,
        "patientName": "Jane Doe",
        "avgBpm": 142,
        "minBpm": 125,
        "maxBpm": 160,
        "duration": 300,
        "classification": "Normal",
        "sharedWithDoctor": false,
        "doctorId": null,
        "timestamp": "2024-01-15T10:30:00.000Z"
      },
      {
        "id": 122,
        "patientId": 1,
        "patientName": "Jane Doe",
        "avgBpm": 138,
        "minBpm": 120,
        "maxBpm": 155,
        "duration": 300,
        "classification": "Normal",
        "sharedWithDoctor": true,
        "doctorId": 5,
        "doctorName": "Dr. Smith",
        "timestamp": "2024-01-14T14:20:00.000Z"
      }
    ],
    "pagination": {
      "total": 45,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  },
  "message": "Monitoring history retrieved successfully"
}
```

### 4.3 Get Monitoring History (for Doctor)
**Endpoint:** `GET /monitoring/doctor-history`

**Headers:**
```
Authorization: Bearer {token}
```

**Query Parameters:**
```
?doctorId=5&limit=20&offset=0&sortBy=timestamp&order=desc
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 122,
        "patientId": 1,
        "patientName": "Jane Doe",
        "avgBpm": 138,
        "minBpm": 120,
        "maxBpm": 155,
        "duration": 300,
        "classification": "Normal",
        "sharedWithDoctor": true,
        "doctorId": 5,
        "timestamp": "2024-01-14T14:20:00.000Z"
      },
      {
        "id": 115,
        "patientId": 3,
        "patientName": "Sarah Johnson",
        "avgBpm": 165,
        "minBpm": 155,
        "maxBpm": 180,
        "duration": 300,
        "classification": "Tachycardia",
        "sharedWithDoctor": true,
        "doctorId": 5,
        "timestamp": "2024-01-13T09:15:00.000Z"
      }
    ],
    "pagination": {
      "total": 28,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  },
  "message": "Doctor monitoring history retrieved successfully"
}
```

### 4.4 Share Monitoring Result to Doctor
**Endpoint:** `POST /monitoring/share`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "monitoringResultId": 123,
  "doctorId": 5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "sharedWithDoctor": true,
    "doctorId": 5,
    "sharedAt": "2024-01-15T11:00:00.000Z"
  },
  "message": "Monitoring result shared with doctor successfully"
}
```

---

## 5. Additional Requirements

### 5.1 CORS Configuration
Backend harus mengaktifkan CORS untuk domain aplikasi Flutter:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
```

### 5.2 File Upload Configuration
- **Upload Directory:** `/uploads/profiles/`
- **File Naming Convention:** `{role}_{userId}_{timestamp}.{ext}`
  - Example: `patient_456_1705320000.jpg`
  - Example: `doctor_123_1705320000.jpg`
- **Image Processing:**
  - Resize images to max 800x800px (maintain aspect ratio)
  - Convert to JPEG with 85% quality
  - Remove EXIF data for privacy
- **Storage:** 
  - Store files in permanent storage (not temp)
  - Make files publicly accessible via URL
  - Consider using CDN for better performance

### 5.3 Security Requirements
1. **Authentication:**
   - Use JWT tokens with expiration (recommended: 24 hours)
   - Implement refresh token mechanism
   - Validate token on every request

2. **Authorization:**
   - Patients can only access their own data
   - Doctors can access data from patients who shared with them
   - Implement role-based access control (RBAC)

3. **Data Validation:**
   - Validate all input data
   - Sanitize file uploads
   - Prevent SQL injection and XSS attacks

4. **Rate Limiting:**
   - Implement rate limiting to prevent abuse
   - Suggested: 100 requests per minute per user

### 5.4 Error Response Format
Semua error harus mengikuti format standar:

**4xx Client Errors:**
```json
{
  "success": false,
  "message": "Error message here",
  "errors": {
    "field1": "Error description",
    "field2": "Error description"
  }
}
```

**5xx Server Errors:**
```json
{
  "success": false,
  "message": "Internal server error",
  "errorCode": "ERR_500"
}
```

### 5.5 Response Time Requirements
- GET requests: < 200ms (average)
- POST/PUT requests: < 500ms (average)
- File uploads: < 2 seconds (for 5MB file)

---

## 6. Testing Checklist

Backend engineer harus memastikan:

- [ ] Semua endpoint dapat diakses dengan authentication yang benar
- [ ] Error handling untuk authentication gagal (401 Unauthorized)
- [ ] Error handling untuk authorization gagal (403 Forbidden)
- [ ] Validation untuk semua input data
- [ ] File upload dengan berbagai format (jpg, jpeg, png)
- [ ] File upload dengan ukuran melebihi limit (error handling)
- [ ] Profile photo URL dapat diakses melalui browser
- [ ] CORS configuration untuk cross-origin requests
- [ ] Database transaction untuk data consistency
- [ ] Pagination untuk history endpoint
- [ ] Filter dan sorting untuk history endpoint
- [ ] Soft delete untuk data (jangan hard delete)
- [ ] Logging untuk semua API requests
- [ ] Performance testing untuk high load

---

## 7. Database Schema Recommendations

### Table: patients
```sql
CREATE TABLE patients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  hpht DATE,
  birth_date DATE,
  address TEXT,
  medical_note TEXT,
  profile_photo_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Table: doctors
```sql
CREATE TABLE doctors (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  specialization VARCHAR(255),
  profile_photo_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Table: monitoring_results
```sql
CREATE TABLE monitoring_results (
  id INT PRIMARY KEY AUTO_INCREMENT,
  patient_id INT NOT NULL,
  avg_bpm INT NOT NULL,
  min_bpm INT NOT NULL,
  max_bpm INT NOT NULL,
  duration INT NOT NULL,
  classification VARCHAR(50),
  data_points JSON,
  shared_with_doctor BOOLEAN DEFAULT FALSE,
  doctor_id INT,
  timestamp TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
  INDEX idx_patient_timestamp (patient_id, timestamp),
  INDEX idx_doctor_timestamp (doctor_id, timestamp)
);
```

---

## 8. API Documentation Tools

Recommended tools untuk dokumentasi API:
1. **Swagger/OpenAPI** - Generate interactive API documentation
2. **Postman Collection** - Share API collection for testing
3. **API Blueprint** - Markdown-based API documentation

---

## 9. Contact & Questions

Jika ada pertanyaan atau klarifikasi terkait API requirements ini, silakan hubungi:
- Frontend Team Lead
- Project Manager

**Dokumen ini akan di-update seiring dengan perkembangan aplikasi.**

---

**Versi:** 1.0  
**Tanggal:** 19 Januari 2025  
**Status:** Ready for Implementation
