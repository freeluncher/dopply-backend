from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.medical import User, Patient, Record, Notification, DoctorPatientAssociation, NotificationStatus, UserRole
from app.core.time_utils import get_local_now
import json

class MonitoringService:
    """Service sederhana untuk monitoring sesuai FIX.md"""
    
    @staticmethod
    def classify_bpm(bpm_data: List[int], gestational_age: int) -> str:
        """Klasifikasi sederhana BPM berdasarkan rata-rata"""
        if not bpm_data:
            return "unclassified"
        
        average_bpm = sum(bpm_data) / len(bpm_data)
        
        # Klasifikasi sederhana berdasarkan usia kehamilan
        if gestational_age >= 20:
            if average_bpm < 110:
                return "bradikardia"
            elif average_bpm > 160:
                return "takikardia"
            else:
                return "normal"
            # Ambil info dokter jika ada
            doctor_id = getattr(record, "doctor_id", None)
            doctor_name = None
            doctor_email = None
        # ...existing code...
    @staticmethod
    def get_monitoring_history(db: Session, user_id: int, user_role: str, 
                              patient_id: Optional[int] = None, 
                              skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Ambil riwayat monitoring berdasarkan role"""
        
        query = db.query(Record).join(Patient)
        
        if user_role == "patient":
            # Pasien hanya bisa lihat recordnya sendiri
            patient = db.query(Patient).filter(Patient.user_id == user_id).first()
            if not patient:
                return {"records": [], "total_count": 0}
            query = query.filter(Record.patient_id == patient.id)
            
        elif user_role == "doctor":
            # Dokter bisa lihat record pasien yang ditugaskan atau yang dia buat
            if patient_id:
                query = query.filter(Record.patient_id == patient_id)
            else:
                # Ambil semua pasien yang ditugaskan ke dokter ini
                assigned_patient_ids = db.query(DoctorPatientAssociation.patient_id).filter(
                    DoctorPatientAssociation.doctor_id == user_id
                ).subquery()
                query = query.filter(
                    (Record.patient_id.in_(assigned_patient_ids)) | 
                    (Record.created_by == user_id)
                )
        
        total_count = query.count()
        records = query.order_by(Record.start_time.desc()).offset(skip).limit(limit).all()
        
        record_list = []
        for record in records:
            patient = db.query(Patient).filter(Patient.id == record.patient_id).first()
            
            # Hitung average BPM
            average_bpm = 0.0
            if record.bpm_data:
                try:
                    bpm_data = record.bpm_data
                    if isinstance(bpm_data, str):
                        bpm_data = json.loads(bpm_data)
                    if isinstance(bpm_data, list) and bpm_data:
                        average_bpm = sum(bpm_data) / len(bpm_data)
                except:
                    pass
            
            # Ambil info dokter jika record sudah dibagikan ke dokter
            doctor_id = getattr(record, "doctor_id", None)
            shared_with_id = getattr(record, "shared_with", None)
            doctor_name = None
            doctor_email = None
            # Prioritaskan shared_with jika ada
            if shared_with_id:
                doctor = db.query(User).filter(User.id == shared_with_id).first()
                if doctor:
                    doctor_name = doctor.name
                    doctor_email = doctor.email
            elif doctor_id:
                doctor = db.query(User).filter(User.id == doctor_id).first()
                if doctor:
                    doctor_name = doctor.name
                    doctor_email = doctor.email
            record_list.append({
                "id": record.id,
                "patient_name": patient.name if patient else "Unknown",
                "doctor_id": shared_with_id or doctor_id,
                "doctor_name": doctor_name,
                "doctor_email": doctor_email,
                "start_time": record.start_time,
                "classification": record.classification or "unclassified",
                "average_bpm": average_bpm,
                "gestational_age": record.gestational_age or 0,
                "notes": record.notes or "",
                "doctor_notes": record.doctor_notes or "",
                "shared_with_doctor": bool(record.shared_with)
            })
        
        return {
            "records": record_list,
            "total_count": total_count
        }
    
    @staticmethod
    def share_monitoring_with_doctor(db: Session, record_id: int, doctor_id: int, 
                                   patient_id: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Share hasil monitoring dengan dokter"""
        
        # Update record
        record = db.query(Record).filter(Record.id == record_id).first()
        if not record:
            raise ValueError("Record tidak ditemukan")
        
        record.shared_with = doctor_id
        
        # Buat notifikasi untuk dokter
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        message = f"Pasien {patient.name} membagikan hasil monitoring. {notes or ''}"
        
        notification = Notification(
            from_patient_id=patient_id,
            to_doctor_id=doctor_id,
            record_id=record_id,
            message=message,
            status=NotificationStatus.unread
        )
        
        db.add(notification)
        db.commit()
        
        return {
            "message": "Hasil monitoring berhasil dibagikan ke dokter",
            "shared_at": get_local_now(),
            "notification_id": notification.id
        }
    
    @staticmethod
    def get_doctor_patients(db: Session, doctor_id: int) -> List[Dict[str, Any]]:
        """Ambil daftar pasien dokter"""
        
        assignments = db.query(DoctorPatientAssociation).filter(
            DoctorPatientAssociation.doctor_id == doctor_id
        ).all()
        
        patient_list = []
        for assignment in assignments:
            patient = db.query(Patient).filter(Patient.id == assignment.patient_id).first()
            if patient:
                # Hitung usia kehamilan jika ada HPHT
                gestational_age_weeks = None
                if patient.hpht:
                    days_diff = (datetime.now().date() - patient.hpht).days
                    gestational_age_weeks = days_diff // 7
                
                # Ambil monitoring terakhir
                last_record = db.query(Record).filter(
                    Record.patient_id == patient.id
                ).order_by(Record.start_time.desc()).first()
                
                patient_list.append({
                    "id": patient.id,
                    "name": patient.name,
                    "email": patient.email,
                    "hpht": patient.hpht,
                    "gestational_age_weeks": gestational_age_weeks,
                    "last_monitoring": last_record.start_time if last_record else None
                })
        
        return patient_list
    
    @staticmethod
    def add_patient_to_doctor(db: Session, doctor_id: int, patient_email: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Dokter menambahkan pasien berdasarkan email"""
        
        # Cari user berdasarkan email
        user = db.query(User).filter(User.email == patient_email, User.role == "patient").first()
        if not user:
            raise ValueError("Pasien dengan email tersebut tidak ditemukan")
        
        # Cari patient record
        patient = db.query(Patient).filter(Patient.user_id == user.id).first()
        if not patient:
            raise ValueError("Data pasien tidak ditemukan")
        
        # Cek apakah sudah ada assignment
        existing = db.query(DoctorPatientAssociation).filter(
            DoctorPatientAssociation.doctor_id == doctor_id,
            DoctorPatientAssociation.patient_id == patient.id
        ).first()
        
        if existing:
            raise ValueError("Pasien sudah ditugaskan ke dokter ini")
        
        # Buat assignment baru
        assignment = DoctorPatientAssociation(
            doctor_id=doctor_id,
            patient_id=patient.id
        )
        
        db.add(assignment)
        db.commit()
        
        return {
            "success": True,
            "message": f"Pasien {patient.name} berhasil ditambahkan",
            "patient_name": patient.name
        }
    
    @staticmethod
    def get_doctor_notifications(db: Session, doctor_id: int, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Ambil notifikasi dokter"""
        
        query = db.query(Notification).filter(Notification.to_doctor_id == doctor_id)
        
        total_count = query.count()
        unread_count = query.filter(Notification.status == NotificationStatus.unread).count()
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        notification_list = []
        for notif in notifications:
            patient = db.query(Patient).filter(Patient.id == notif.from_patient_id).first()
            
            notification_list.append({
                "id": notif.id,
                "from_patient_name": patient.name if patient else "Unknown",
                "record_id": notif.record_id,
                "message": notif.message,
                "created_at": notif.created_at,
                "is_read": notif.status == NotificationStatus.read
            })
        
        return {
            "notifications": notification_list,
            "unread_count": unread_count
        }
    
    @staticmethod
    def mark_notification_read(db: Session, notification_id: int, doctor_id: int) -> Dict[str, Any]:
        """Tandai notifikasi sebagai sudah dibaca"""
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.to_doctor_id == doctor_id
        ).first()
        
        if not notification:
            raise ValueError("Notifikasi tidak ditemukan")
        
        notification.status = NotificationStatus.read
        db.commit()
        
        return {
            "success": True,
            "message": "Notifikasi ditandai sebagai sudah dibaca"
        }
    
    @staticmethod
    def verify_doctor(db: Session, admin_user_id: int, doctor_user_id: int) -> Dict[str, Any]:
        """Admin memverifikasi dokter"""
        
        # Cek apakah user adalah admin
        admin = db.query(User).filter(User.id == admin_user_id, User.role == "admin").first()
        if not admin:
            raise ValueError("Akses ditolak: Bukan admin")
        
        # Cari doctor user
        doctor_user = db.query(User).filter(
            User.id == doctor_user_id, 
            User.role == UserRole.doctor
        ).first()
        if not doctor_user:
            raise ValueError("User dokter tidak ditemukan")
        
        # Set doctor as verified
        doctor_user.is_verified = True
        
        db.commit()
        
        doctor_user = db.query(User).filter(User.id == doctor_user_id).first()
        
        return {
            "success": True,
            "message": f"Dokter {doctor_user.name} berhasil diverifikasi",
            "doctor_name": doctor_user.name
        }
