# 📱 PERINTAH FRONTEND - HAPUS DAN REBUILD MONITORING
*Detailed Frontend Commands for Removal and Rebuild*

## 📋 LANGKAH-LANGKAH FRONTEND

### STEP 1: BACKUP DAN PERSIAPAN

```bash
# 1. Backup existing monitoring files
mkdir backup_monitoring_$(date +%Y%m%d)
cp -r lib/screens/monitoring backup_monitoring_$(date +%Y%m%d)/
cp -r lib/services/monitoring backup_monitoring_$(date +%Y%m%d)/
cp -r lib/models/monitoring backup_monitoring_$(date +%Y%m%d)/

# 2. Commit current state
git add .
git commit -m "Backup: Before monitoring system rebuild"
```

### STEP 2: REMOVE OLD MONITORING FEATURES

#### A. Remove Old Screens:
```dart
// HAPUS files/screens ini:
- lib/screens/monitoring/pregnancy_info_screen.dart
- lib/screens/monitoring/complex_session_screen.dart
- lib/screens/monitoring/old_monitoring_history_screen.dart
- lib/screens/monitoring/session_details_screen.dart
- lib/screens/monitoring/share_session_screen.dart

// HAPUS dari navigation/routing
- Semua routes ke screens yang dihapus
- Complex monitoring flow navigation
```

#### B. Remove Old Models:
```dart
// HAPUS models ini:
- lib/models/pregnancy_info.dart
- lib/models/monitoring_session.dart
- lib/models/complex_monitoring_result.dart
- lib/models/session_sharing.dart

// HAPUS dari barrel exports (index.dart)
```

#### C. Remove Old Services:
```dart
// HAPUS methods ini dari lib/services/monitoring_service.dart:
- createMonitoringSession()
- getMonitoringSessions()
- getSessionDetails()
- shareSessionWithDoctor()
- createPregnancyInfo()
- updatePregnancyInfo()
- getPregnancyInfo()

// Atau hapus file completely dan buat ulang
```

### STEP 3: CREATE NEW MODELS

```dart
// CREATE: lib/models/esp32_monitoring.dart

class ESP32MonitoringRequest {
  final int patientId;
  final int gestationalAge;
  final List<int> bpmReadings;
  final double? monitoringDuration;
  final String? notes;

  const ESP32MonitoringRequest({
    required this.patientId,
    required this.gestationalAge,
    required this.bpmReadings,
    this.monitoringDuration,
    this.notes,
  });

  Map<String, dynamic> toJson() => {
    'patient_id': patientId,
    'gestational_age': gestationalAge,
    'bpm_readings': bpmReadings,
    'monitoring_duration': monitoringDuration,
    'notes': notes,
  };
}

class MonitoringClassificationResult {
  final String classification;
  final double averageBpm;
  final String riskLevel;
  final List<String> recommendations;
  final double variability;
  final int minBpm;
  final int maxBpm;
  final int totalReadings;
  final bool isIrregular;
  final Map<String, int> normalRange;

  const MonitoringClassificationResult({
    required this.classification,
    required this.averageBpm,
    required this.riskLevel,
    required this.recommendations,
    required this.variability,
    required this.minBpm,
    required this.maxBpm,
    required this.totalReadings,
    required this.isIrregular,
    required this.normalRange,
  });

  factory MonitoringClassificationResult.fromJson(Map<String, dynamic> json) {
    return MonitoringClassificationResult(
      classification: json['classification'],
      averageBpm: json['average_bpm'].toDouble(),
      riskLevel: json['risk_level'],
      recommendations: List<String>.from(json['recommendations']),
      variability: json['variability'].toDouble(),
      minBpm: json['min_bpm'],
      maxBpm: json['max_bpm'],
      totalReadings: json['total_readings'],
      isIrregular: json['is_irregular'],
      normalRange: Map<String, int>.from(json['normal_range']),
    );
  }

  Color get classificationColor {
    switch (classification.toLowerCase()) {
      case 'normal':
        return Colors.green;
      case 'bradycardia':
      case 'tachycardia':
        return Colors.red;
      case 'irregular':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData get classificationIcon {
    switch (classification.toLowerCase()) {
      case 'normal':
        return Icons.favorite;
      case 'bradycardia':
        return Icons.trending_down;
      case 'tachycardia':
        return Icons.trending_up;
      case 'irregular':
        return Icons.warning;
      default:
        return Icons.help;
    }
  }
}

class ESP32MonitoringResponse {
  final bool success;
  final String message;
  final int recordId;
  final MonitoringClassificationResult classificationResult;

  const ESP32MonitoringResponse({
    required this.success,
    required this.message,
    required this.recordId,
    required this.classificationResult,
  });

  factory ESP32MonitoringResponse.fromJson(Map<String, dynamic> json) {
    return ESP32MonitoringResponse(
      success: json['success'],
      message: json['message'],
      recordId: json['record_id'],
      classificationResult: MonitoringClassificationResult.fromJson(
        json['classification_result']
      ),
    );
  }
}

class MonitoringRecord {
  final int id;
  final int patientId;
  final int? doctorId;
  final String monitoringType;
  final int gestationalAge;
  final DateTime startTime;
  final DateTime? endTime;
  final double monitoringDuration;
  final String classification;
  final double averageBpm;
  final String notes;
  final String doctorNotes;
  final bool sharedWithDoctor;
  final DateTime createdAt;

  const MonitoringRecord({
    required this.id,
    required this.patientId,
    this.doctorId,
    required this.monitoringType,
    required this.gestationalAge,
    required this.startTime,
    this.endTime,
    required this.monitoringDuration,
    required this.classification,
    required this.averageBpm,
    required this.notes,
    required this.doctorNotes,
    required this.sharedWithDoctor,
    required this.createdAt,
  });

  factory MonitoringRecord.fromJson(Map<String, dynamic> json) {
    return MonitoringRecord(
      id: json['id'],
      patientId: json['patient_id'],
      doctorId: json['doctor_id'],
      monitoringType: json['monitoring_type'],
      gestationalAge: json['gestational_age'],
      startTime: DateTime.parse(json['start_time']),
      endTime: json['end_time'] != null ? DateTime.parse(json['end_time']) : null,
      monitoringDuration: json['monitoring_duration'].toDouble(),
      classification: json['classification'],
      averageBpm: json['average_bpm']?.toDouble() ?? 0.0,
      notes: json['notes'] ?? '',
      doctorNotes: json['doctor_notes'] ?? '',
      sharedWithDoctor: json['shared_with_doctor'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class AssignedPatient {
  final int patientId;
  final String patientName;
  final String assignedDate;
  final String status;
  final String contactInfo;

  const AssignedPatient({
    required this.patientId,
    required this.patientName,
    required this.assignedDate,
    required this.status,
    required this.contactInfo,
  });

  factory AssignedPatient.fromJson(Map<String, dynamic> json) {
    return AssignedPatient(
      patientId: json['patient_id'],
      patientName: json['patient_name'],
      assignedDate: json['assigned_date'],
      status: json['status'],
      contactInfo: json['contact_info'],
    );
  }
}
```

### STEP 4: CREATE NEW SERVICES

```dart
// CREATE: lib/services/esp32_monitoring_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/esp32_monitoring.dart';
import '../config/api_config.dart';

class ESP32MonitoringService {
  final _storage = FlutterSecureStorage();
  final String baseUrl = ApiConfig.baseUrl;

  // Process ESP32 monitoring data
  Future<ESP32MonitoringResponse> processMonitoringData({
    required int patientId,
    required int gestationalAge,
    required List<int> bpmReadings,
    double? monitoringDuration,
    String? notes,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) throw Exception('No authentication token');

      final request = ESP32MonitoringRequest(
        patientId: patientId,
        gestationalAge: gestationalAge,
        bpmReadings: bpmReadings,
        monitoringDuration: monitoringDuration,
        notes: notes,
      );

      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/fetal-monitoring/monitoring/process'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ESP32MonitoringResponse.fromJson(data);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to process monitoring data');
      }
    } catch (e) {
      throw Exception('Error processing monitoring data: $e');
    }
  }

  // Get monitoring history
  Future<List<MonitoringRecord>> getMonitoringHistory({
    int? patientId,
    int skip = 0,
    int limit = 20,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) throw Exception('No authentication token');

      final queryParams = {
        'skip': skip.toString(),
        'limit': limit.toString(),
      };
      if (patientId != null) {
        queryParams['patient_id'] = patientId.toString();
      }

      final uri = Uri.parse('$baseUrl/api/v1/fetal-monitoring/monitoring/history')
          .replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> recordsData = data['data'];
        return recordsData.map((json) => MonitoringRecord.fromJson(json)).toList();
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to get monitoring history');
      }
    } catch (e) {
      throw Exception('Error getting monitoring history: $e');
    }
  }

  // Share monitoring with doctor (patient only)
  Future<void> shareMonitoringWithDoctor({
    required int recordId,
    required int doctorId,
    String? notes,
  }) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) throw Exception('No authentication token');

      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/fetal-monitoring/monitoring/share'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'record_id': recordId,
          'doctor_id': doctorId,
          'notes': notes,
        }),
      );

      if (response.statusCode != 200) {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to share monitoring');
      }
    } catch (e) {
      throw Exception('Error sharing monitoring: $e');
    }
  }

  // Get assigned patients for doctor
  Future<List<AssignedPatient>> getAssignedPatientsForDoctor(int doctorId) async {
    try {
      final token = await _storage.read(key: 'auth_token');
      if (token == null) throw Exception('No authentication token');

      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/fetal-monitoring/doctors/$doctorId/assigned-patients'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List<dynamic> patientsData = data['patients'];
        return patientsData.map((json) => AssignedPatient.fromJson(json)).toList();
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to get assigned patients');
      }
    } catch (e) {
      throw Exception('Error getting assigned patients: $e');
    }
  }
}
```

### STEP 5: CREATE ESP32 SERVICE

```dart
// CREATE: lib/services/esp32_connection_service.dart

import 'dart:async';
import 'dart:math';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';

class ESP32ConnectionService {
  BluetoothConnection? _connection;
  StreamSubscription<Uint8List>? _dataSubscription;
  final StreamController<int> _bpmController = StreamController<int>.broadcast();
  final StreamController<bool> _connectionController = StreamController<bool>.broadcast();
  
  bool _isConnected = false;
  bool _isMonitoring = false;
  List<int> _bpmReadings = [];

  // Streams
  Stream<int> get bpmStream => _bmpController.stream;
  Stream<bool> get connectionStream => _connectionController.stream;
  
  // Getters
  bool get isConnected => _isConnected;
  bool get isMonitoring => _isMonitoring;
  List<int> get bpmReadings => List.unmodifiable(_bpmReadings);

  // Connect to ESP32
  Future<bool> connectToESP32({String? deviceAddress}) async {
    try {
      // For demo, we'll simulate connection
      // In real implementation, replace with actual Bluetooth connection
      
      await Future.delayed(Duration(seconds: 2)); // Simulate connection time
      
      _isConnected = true;
      _connectionController.add(true);
      
      // Start listening for demo data
      _startDemoDataStream();
      
      return true;
    } catch (e) {
      _isConnected = false;
      _connectionController.add(false);
      throw Exception('Failed to connect to ESP32: $e');
    }
  }

  // Start monitoring
  void startMonitoring() {
    if (!_isConnected) {
      throw Exception('Not connected to ESP32');
    }
    
    _isMonitoring = true;
    _bpmReadings.clear();
  }

  // Stop monitoring
  void stopMonitoring() {
    _isMonitoring = false;
  }

  // Disconnect
  Future<void> disconnect() async {
    _isMonitoring = false;
    _dataSubscription?.cancel();
    await _connection?.close();
    _connection = null;
    _isConnected = false;
    _connectionController.add(false);
  }

  // Demo data stream (replace with real ESP32 data parsing)
  void _startDemoDataStream() {
    Timer.periodic(Duration(seconds: 1), (timer) {
      if (!_isConnected) {
        timer.cancel();
        return;
      }
      
      if (_isMonitoring) {
        // Generate realistic fetal heart rate data (120-160 BPM normal range)
        final random = Random();
        final baseBpm = 140;
        final variation = random.nextInt(20) - 10; // -10 to +10 variation
        final bpm = baseBpm + variation;
        
        _bpmReadings.add(bpm);
        _bpmController.add(bpm);
      }
    });
  }

  // Real ESP32 data parsing (implement based on your ESP32 protocol)
  void _parseESP32Data(Uint8List data) {
    try {
      // Example: Parse BPM from ESP32 data
      // Implement based on your ESP32 communication protocol
      String dataString = String.fromCharCodes(data);
      
      // Example protocol: "BPM:140\n"
      if (dataString.startsWith('BPM:')) {
        final bpmString = dataString.substring(4).trim();
        final bpm = int.tryParse(bpmString);
        
        if (bpm != null && _isMonitoring) {
          _bpmReadings.add(bpm);
          _bmpController.add(bpm);
        }
      }
    } catch (e) {
      print('Error parsing ESP32 data: $e');
    }
  }

  // Dispose
  void dispose() {
    _dataSubscription?.cancel();
    _bmpController.close();
    _connectionController.close();
    disconnect();
  }
}
```

### STEP 6: CREATE NEW SCREENS

#### A. Doctor Patient Selection Screen:

```dart
// CREATE: lib/screens/monitoring/doctor_patient_selection_screen.dart

import 'package:flutter/material.dart';
import '../../models/esp32_monitoring.dart';
import '../../services/esp32_monitoring_service.dart';
import '../../services/auth_service.dart';
import 'esp32_connection_screen.dart';

class DoctorPatientSelectionScreen extends StatefulWidget {
  @override
  _DoctorPatientSelectionScreenState createState() => _DoctorPatientSelectionScreenState();
}

class _DoctorPatientSelectionScreenState extends State<DoctorPatientSelectionScreen> {
  final ESP32MonitoringService _monitoringService = ESP32MonitoringService();
  final AuthService _authService = AuthService();
  
  List<AssignedPatient> _patients = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAssignedPatients();
  }

  Future<void> _loadAssignedPatients() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final currentUser = await _authService.getCurrentUser();
      if (currentUser == null) {
        throw Exception('User not found');
      }

      final patients = await _monitoringService.getAssignedPatientsForDoctor(currentUser.id);
      
      setState(() {
        _patients = patients;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  void _selectPatient(AssignedPatient patient) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ESP32ConnectionScreen(
          selectedPatient: patient,
          userRole: 'doctor',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Pilih Pasien untuk Monitoring'),
        backgroundColor: Colors.blue,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(_error!, style: TextStyle(color: Colors.red)),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadAssignedPatients,
              child: Text('Coba Lagi'),
            ),
          ],
        ),
      );
    }

    if (_patients.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.people_outline, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('Tidak ada pasien yang ditugaskan'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadAssignedPatients,
              child: Text('Refresh'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadAssignedPatients,
      child: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: _patients.length,
        itemBuilder: (context, index) {
          final patient = _patients[index];
          return Card(
            margin: EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: Colors.blue,
                child: Icon(Icons.person, color: Colors.white),
              ),
              title: Text(
                patient.patientName,
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Ditugaskan: ${patient.assignedDate}'),
                  Text('Status: ${patient.status}'),
                  Text('Kontak: ${patient.contactInfo}'),
                ],
              ),
              trailing: Icon(Icons.arrow_forward_ios),
              onTap: () => _selectPatient(patient),
            ),
          );
        },
      ),
    );
  }
}
```

#### B. ESP32 Connection Screen:

```dart
// CREATE: lib/screens/monitoring/esp32_connection_screen.dart

import 'package:flutter/material.dart';
import '../../models/esp32_monitoring.dart';
import '../../services/esp32_connection_service.dart';
import 'monitoring_screen.dart';

class ESP32ConnectionScreen extends StatefulWidget {
  final AssignedPatient? selectedPatient;
  final String userRole;

  const ESP32ConnectionScreen({
    Key? key,
    this.selectedPatient,
    required this.userRole,
  }) : super(key: key);

  @override
  _ESP32ConnectionScreenState createState() => _ESP32ConnectionScreenState();
}

class _ESP32ConnectionScreenState extends State<ESP32ConnectionScreen> {
  final ESP32ConnectionService _esp32Service = ESP32ConnectionService();
  
  bool _isConnecting = false;
  bool _isConnected = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _esp32Service.connectionStream.listen((connected) {
      setState(() {
        _isConnected = connected;
        _isConnecting = false;
      });
    });
  }

  Future<void> _connectToESP32() async {
    setState(() {
      _isConnecting = true;
      _error = null;
    });

    try {
      await _esp32Service.connectToESP32();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isConnecting = false;
      });
    }
  }

  void _startMonitoring() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MonitoringScreen(
          esp32Service: _esp32Service,
          selectedPatient: widget.selectedPatient,
          userRole: widget.userRole,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Koneksi ESP32'),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (widget.selectedPatient != null) ...[
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Text('Pasien Terpilih:', style: TextStyle(fontSize: 16)),
                      SizedBox(height: 8),
                      Text(
                        widget.selectedPatient!.patientName,
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 32),
            ],
            
            Icon(
              _isConnected ? Icons.bluetooth_connected : Icons.bluetooth,
              size: 80,
              color: _isConnected ? Colors.green : Colors.grey,
            ),
            SizedBox(height: 16),
            
            Text(
              _isConnected ? 'ESP32 Terhubung' : 'ESP32 Tidak Terhubung',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: _isConnected ? Colors.green : Colors.grey,
              ),
            ),
            SizedBox(height: 32),
            
            if (_error != null) ...[
              Text(
                _error!,
                style: TextStyle(color: Colors.red),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 16),
            ],
            
            if (!_isConnected) ...[
              ElevatedButton(
                onPressed: _isConnecting ? null : _connectToESP32,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
                child: _isConnecting
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text('Hubungkan ESP32', style: TextStyle(fontSize: 16)),
              ),
            ] else ...[
              ElevatedButton(
                onPressed: _startMonitoring,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
                child: Text('Mulai Monitoring', style: TextStyle(fontSize: 16)),
              ),
            ],
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _esp32Service.dispose();
    super.dispose();
  }
}
```

#### C. Monitoring Screen:

```dart
// CREATE: lib/screens/monitoring/monitoring_screen.dart

import 'package:flutter/material.dart';
import 'dart:async';
import '../../models/esp32_monitoring.dart';
import '../../services/esp32_connection_service.dart';
import 'monitoring_results_screen.dart';

class MonitoringScreen extends StatefulWidget {
  final ESP32ConnectionService esp32Service;
  final AssignedPatient? selectedPatient;
  final String userRole;

  const MonitoringScreen({
    Key? key,
    required this.esp32Service,
    this.selectedPatient,
    required this.userRole,
  }) : super(key: key);

  @override
  _MonitoringScreenState createState() => _MonitoringScreenState();
}

class _MonitoringScreenState extends State<MonitoringScreen> {
  bool _isMonitoring = false;
  int _currentBpm = 0;
  List<int> _bpmHistory = [];
  Timer? _monitoringTimer;
  int _elapsedSeconds = 0;
  
  StreamSubscription<int>? _bpmSubscription;

  @override
  void initState() {
    super.initState();
    _bmpSubscription = widget.esp32Service.bmpStream.listen((bpm) {
      setState(() {
        _currentBmp = bmp;
        if (_isMonitoring) {
          _bmpHistory.add(bmp);
        }
      });
    });
  }

  void _startMonitoring() {
    setState(() {
      _isMonitoring = true;
      _elapsedSeconds = 0;
      _bmpHistory.clear();
    });

    widget.esp32Service.startMonitoring();
    
    _monitoringTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      setState(() {
        _elapsedSeconds++;
      });
    });
  }

  void _stopMonitoring() {
    setState(() {
      _isMonitoring = false;
    });

    widget.esp32Service.stopMonitoring();
    _monitoringTimer?.cancel();
    
    // Navigate to results screen
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => MonitoringResultsScreen(
          bmpReadings: List.from(_bmpHistory),
          monitoringDuration: _elapsedSeconds / 60.0,
          selectedPatient: widget.selectedPatient,
          userRole: widget.userRole,
        ),
      ),
    );
  }

  String _formatDuration(int seconds) {
    final minutes = seconds ~/ 60;
    final remainingSeconds = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${remainingSeconds.toString().padLeft(2, '0')}';
  }

  Color _getBpmColor(int bpm) {
    if (bpm >= 110 && bpm <= 160) {
      return Colors.green;
    } else if (bpm < 110) {
      return Colors.blue;
    } else {
      return Colors.red;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Monitoring Fetal'),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            if (widget.selectedPatient != null) ...[
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.person, color: Colors.blue),
                      SizedBox(width: 8),
                      Text(
                        widget.selectedPatient!.patientName,
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 16),
            ],
            
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // BPM Display
                  Container(
                    width: 200,
                    height: 200,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _getBmpColor(_currentBmp).withOpacity(0.1),
                      border: Border.all(
                        color: _getBmpColor(_currentBmp),
                        width: 4,
                      ),
                    ),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          '$_currentBmp',
                          style: TextStyle(
                            fontSize: 48,
                            fontWeight: FontWeight.bold,
                            color: _getBmpColor(_currentBmp),
                          ),
                        ),
                        Text(
                          'BPM',
                          style: TextStyle(
                            fontSize: 16,
                            color: _getBmpColor(_currentBmp),
                          ),
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 32),
                  
                  // Timer
                  Text(
                    _formatDuration(_elapsedSeconds),
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 16),
                  
                  Text(
                    'Total Readings: ${_bmpHistory.length}',
                    style: TextStyle(fontSize: 16),
                  ),
                  SizedBox(height: 32),
                  
                  // Control Button
                  ElevatedButton(
                    onPressed: _isMonitoring ? _stopMonitoring : _startMonitoring,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _isMonitoring ? Colors.red : Colors.green,
                      padding: EdgeInsets.symmetric(horizontal: 48, vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(25),
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          _isMonitoring ? Icons.stop : Icons.play_arrow,
                          size: 24,
                        ),
                        SizedBox(width: 8),
                        Text(
                          _isMonitoring ? 'Stop Monitoring' : 'Start Monitoring',
                          style: TextStyle(fontSize: 18),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _bmpSubscription?.cancel();
    _monitoringTimer?.cancel();
    super.dispose();
  }
}
```

### STEP 7: UPDATE NAVIGATION

```dart
// UPDATE: lib/main.dart routes

import 'screens/monitoring/doctor_patient_selection_screen.dart';
import 'screens/monitoring/esp32_connection_screen.dart';
import 'screens/monitoring/monitoring_screen.dart';
import 'screens/monitoring/monitoring_results_screen.dart';
import 'screens/monitoring/monitoring_history_screen.dart';

// Add routes:
'/doctor-patient-selection': (context) => DoctorPatientSelectionScreen(),
'/esp32-connection': (context) => ESP32ConnectionScreen(userRole: 'patient'),
'/monitoring-history': (context) => MonitoringHistoryScreen(),
```

### STEP 8: UPDATE MAIN NAVIGATION

```dart
// UPDATE: Doctor dashboard navigation
if (userRole == 'doctor') {
  Navigator.pushNamed(context, '/doctor-patient-selection');
}

// UPDATE: Patient monitoring navigation  
if (userRole == 'patient') {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => ESP32ConnectionScreen(userRole: 'patient'),
    ),
  );
}
```

---

## ✅ FRONTEND TESTING CHECKLIST

### Doctor Flow:
- [ ] Patient selection screen loads assigned patients
- [ ] ESP32 connection works
- [ ] Monitoring screen receives BPM data
- [ ] Results screen shows classification
- [ ] Notes can be added
- [ ] Data saves successfully
- [ ] History screen shows records

### Patient Flow:
- [ ] ESP32 connection works directly
- [ ] Monitoring screen receives BPM data  
- [ ] Results screen shows classification
- [ ] Data saves successfully
- [ ] History screen shows records
- [ ] Sharing with doctor works

### Integration:
- [ ] API calls work correctly
- [ ] Error handling works
- [ ] Loading states work
- [ ] Navigation flows work
- [ ] Real-time BPM updates work

**RESULT**: Complete rebuilt monitoring system with ESP32 integration! 🎯
