# Service untuk Fetal Monitoring Classification dan Business Logic
from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics
from app.models.medical import FetalClassification, RiskLevel, OverallClassification

class FetalMonitoringService:
    """Service untuk classification dan business logic fetal monitoring"""
    
    @staticmethod
    def classify_fetal_bpm(bpm_readings: List[int], gestational_age: int) -> Dict[str, Any]:
        """
        Classify fetal BPM berdasarkan gestational age dan patterns
        
        Args:
            bpm_readings: List of BPM values
            gestational_age: Gestational age in weeks
            
        Returns:
            Dict containing classification results
        """
        if not bpm_readings:
            raise ValueError("BPM readings cannot be empty")
            
        if not 1 <= gestational_age <= 42:
            raise ValueError("Gestational age must be between 1 and 42 weeks")
            
        # Calculate statistics
        avg_bpm = statistics.mean(bpm_readings)
        
        # Define normal ranges by gestational age
        normal_range = FetalMonitoringService._get_normal_range(gestational_age)
        
        # Primary classification based on average BPM
        primary_classification = FetalMonitoringService._classify_by_average(avg_bpm, normal_range)
        
        # Check for irregularity
        variability = FetalMonitoringService._calculate_variability(bpm_readings)
        is_irregular = FetalMonitoringService._is_irregular_pattern(bpm_readings, variability)
        
        # Final classification
        if is_irregular:
            classification = FetalClassification.irregular
        else:
            classification = primary_classification
            
        # Determine overall classification and risk level
        overall_classification = FetalMonitoringService._determine_overall_classification(
            classification, avg_bpm, normal_range, variability
        )
        
        risk_level = FetalMonitoringService._assess_risk_level(
            classification, avg_bpm, normal_range, variability
        )
        
        # Generate findings and recommendations
        findings = FetalMonitoringService._generate_findings(
            classification, avg_bpm, normal_range, variability, gestational_age
        )
        
        recommendations = FetalMonitoringService._generate_recommendations(
            classification, risk_level, gestational_age
        )
        
        return {
            # Format untuk frontend Flutter
            "classification": overall_classification.value,
            "confidence": 0.92,  # default confidence score
            "risk_factors": findings,
            "recommendations": recommendations,
            
            # Fields tambahan untuk backward compatibility
            "overall_classification": overall_classification.value,
            "average_bpm": round(avg_bpm, 2),
            "baseline_variability": round(variability, 2),
            "findings": findings,
            "risk_level": risk_level.value
        }
    
    @staticmethod
    def _get_normal_range(gestational_age: int) -> tuple:
        """Get normal BPM range for gestational age"""
        if gestational_age < 20:
            return (120, 180)
        elif gestational_age < 32:
            return (115, 170)
        else:
            return (110, 160)
    
    @staticmethod
    def _classify_by_average(avg_bpm: float, normal_range: tuple) -> FetalClassification:
        """Classify based on average BPM"""
        if avg_bpm < normal_range[0]:
            return FetalClassification.bradycardia
        elif avg_bpm > normal_range[1]:
            return FetalClassification.tachycardia
        else:
            return FetalClassification.normal
    
    @staticmethod
    def _calculate_variability(bpm_readings: List[int]) -> float:
        """Calculate baseline variability (standard deviation)"""
        if len(bpm_readings) < 2:
            return 0.0
        return statistics.stdev(bpm_readings)
    
    @staticmethod
    def _is_irregular_pattern(bpm_readings: List[int], variability: float) -> bool:
        """Check if pattern is irregular based on variability and trends"""
        # High variability threshold
        if variability > 25:
            return True
            
        # Check for extreme jumps
        for i in range(1, len(bpm_readings)):
            diff = abs(bpm_readings[i] - bpm_readings[i-1])
            if diff > 40:  # Jump > 40 BPM
                return True
                
        return False
    
    @staticmethod
    def _determine_overall_classification(
        classification: FetalClassification, 
        avg_bpm: float, 
        normal_range: tuple, 
        variability: float
    ) -> OverallClassification:
        """Determine overall classification"""
        if classification == FetalClassification.normal and variability < 15:
            return OverallClassification.normal
        elif classification == FetalClassification.irregular or variability > 20:
            return OverallClassification.abnormal
        else:
            return OverallClassification.concerning
    
    @staticmethod
    def _assess_risk_level(
        classification: FetalClassification,
        avg_bpm: float,
        normal_range: tuple,
        variability: float
    ) -> RiskLevel:
        """Assess risk level"""
        if classification == FetalClassification.normal and variability < 15:
            return RiskLevel.low
        elif classification == FetalClassification.irregular:
            return RiskLevel.high
        elif (classification == FetalClassification.bradycardia and avg_bpm < normal_range[0] - 20) or \
             (classification == FetalClassification.tachycardia and avg_bpm > normal_range[1] + 20):
            return RiskLevel.high
        else:
            return RiskLevel.medium
    
    @staticmethod
    def _generate_findings(
        classification: FetalClassification,
        avg_bpm: float,
        normal_range: tuple,
        variability: float,
        gestational_age: int
    ) -> List[str]:
        """Generate clinical findings"""
        findings = []
        
        findings.append(f"Average fetal heart rate: {avg_bpm:.1f} BPM")
        findings.append(f"Normal range for {gestational_age} weeks: {normal_range[0]}-{normal_range[1]} BPM")
        findings.append(f"Baseline variability: {variability:.1f} BPM")
        
        if classification == FetalClassification.normal:
            findings.append("Normal fetal heart rate pattern")
        elif classification == FetalClassification.bradycardia:
            findings.append("Fetal bradycardia detected")
        elif classification == FetalClassification.tachycardia:
            findings.append("Fetal tachycardia detected")
        elif classification == FetalClassification.irregular:
            findings.append("Irregular fetal heart rate pattern detected")
            
        if variability > 25:
            findings.append("High baseline variability noted")
        elif variability < 5:
            findings.append("Low baseline variability noted")
            
        return findings
    
    @staticmethod
    def _generate_recommendations(
        classification: FetalClassification,
        risk_level: RiskLevel,
        gestational_age: int
    ) -> List[str]:
        """Generate clinical recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.low:
            recommendations.append("Continue regular monitoring")
            recommendations.append("Routine prenatal care")
        elif risk_level == RiskLevel.medium:
            recommendations.append("Increased monitoring frequency")
            recommendations.append("Consult with healthcare provider")
            recommendations.append("Follow-up in 1-2 weeks")
        else:  # High risk
            recommendations.append("Immediate medical evaluation required")
            recommendations.append("Consider continuous monitoring")
            recommendations.append("Urgent obstetric consultation")
            
        if classification == FetalClassification.bradycardia:
            recommendations.append("Monitor for signs of fetal distress")
            recommendations.append("Consider maternal position changes")
        elif classification == FetalClassification.tachycardia:
            recommendations.append("Evaluate for maternal fever or infection")
            recommendations.append("Check maternal hydration status")
        elif classification == FetalClassification.irregular:
            recommendations.append("Extended monitoring session recommended")
            recommendations.append("Consider fetal echocardiography")
            
        return recommendations

    @staticmethod
    def validate_session_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fetal monitoring session data"""
        errors = {}
        
        # Validate gestational age
        gestational_age = session_data.get('gestational_age')
        if not gestational_age or not 1 <= gestational_age <= 42:
            errors['gestational_age'] = "Gestational age must be between 1 and 42 weeks"
        
        # Validate BPM readings
        readings = session_data.get('readings', [])
        if not readings:
            errors['readings'] = "At least one BPM reading is required"
        else:
            for i, reading in enumerate(readings):
                bpm = reading.get('bpm')
                if not bpm or not 60 <= bpm <= 300:
                    errors[f'readings[{i}].bpm'] = "BPM must be between 60 and 300"
                    
                signal_quality = reading.get('signal_quality')
                if signal_quality is not None and not 0.0 <= signal_quality <= 1.0:
                    errors[f'readings[{i}].signal_quality'] = "Signal quality must be between 0.0 and 1.0"
        
        # Validate monitoring type
        monitoring_type = session_data.get('monitoring_type')
        if monitoring_type not in ['clinic', 'home']:
            errors['monitoring_type'] = "Monitoring type must be 'clinic' or 'home'"
            
        return errors
    
    @staticmethod
    def classify_fetal_heart_rate(fhr_data, gestational_age: int, 
                                 maternal_age: Optional[int] = None, duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        """
        Main method for classifying fetal heart rate data (compatible with endpoint)
        
        Args:
            fhr_data: List of integers (BPM values) or List of dicts with FHR data points
            gestational_age: Gestational age in weeks
            maternal_age: Maternal age (optional)
            duration_minutes: Duration of monitoring (optional)
            
        Returns:
            Dict containing classification results
        """
        # Handle both formats: simple integers or complex objects
        if not fhr_data:
            raise ValueError("FHR data cannot be empty")
            
        # Extract BPM values based on input format
        if isinstance(fhr_data[0], int):
            # Simple format: [140, 142, 138, ...]
            bpm_readings = fhr_data
        elif isinstance(fhr_data[0], dict):
            # Complex format: [{"bpm": 140, "timestamp": ...}, ...]
            bpm_readings = [point["bpm"] for point in fhr_data]
        else:
            # Pydantic objects
            bpm_readings = [point.bpm for point in fhr_data]
        
        # Use existing classification logic
        result = FetalMonitoringService.classify_fetal_bpm(bpm_readings, gestational_age)
        
        # Add additional fields expected by endpoint
        result.update({
            "average_bpm": float(statistics.mean(bpm_readings)),
            "baseline_variability": result.get("variability", 0.0)
        })
        
        return result

    @staticmethod
    def save_monitoring_session(db, request, user_id: int) -> Dict[str, Any]:
        """Save a fetal monitoring session"""
        from app.models.medical import FetalMonitoringSession, FetalHeartRateReading, FetalMonitoringResult
        
        # Generate session ID
        session_id = str(int(datetime.now().timestamp() * 1000))
        
        # Create session
        session = FetalMonitoringSession(
            id=session_id,
            patient_id=request.patient_id,
            doctor_id=user_id if hasattr(request, 'doctor_id') and request.doctor_id else None,
            monitoring_type=request.monitoring_type,
            gestational_age=request.gestational_age,
            start_time=request.start_time,
            end_time=request.end_time,
            notes=request.notes,
            doctor_notes=getattr(request, 'doctor_notes', None)
        )
        
        db.add(session)
        db.flush()
        
        # Add readings
        for reading_data in request.readings:
            reading = FetalHeartRateReading(
                session_id=session_id,
                timestamp=reading_data.timestamp,
                bpm=reading_data.bpm,
                signal_quality=reading_data.signal_quality,
                classification=reading_data.classification
            )
            db.add(reading)
        
        # Add result if provided
        if request.result:
            result = FetalMonitoringResult(
                session_id=session_id,
                overall_classification=request.result.overall_classification,
                average_bpm=request.result.average_bpm,
                baseline_variability=request.result.baseline_variability,
                findings=request.result.findings,
                recommendations=request.result.recommendations,
                risk_level=request.result.risk_level
            )
            db.add(result)
        
        db.commit()
        db.refresh(session)
        
        return {
            "id": session_id,
            "patient_id": session.patient_id,
            "doctor_id": session.doctor_id,
            "monitoring_type": session.monitoring_type.value,
            "gestational_age": session.gestational_age,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "notes": session.notes,
            "doctor_notes": session.doctor_notes,
            "shared_with_doctor": session.shared_with_doctor,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "readings": [],
            "result": None
        }
    
    @staticmethod
    def get_monitoring_sessions(db, patient_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """Get fetal monitoring sessions"""
        from app.models.medical import FetalMonitoringSession
        
        query = db.query(FetalMonitoringSession)
        if patient_id:
            query = query.filter(FetalMonitoringSession.patient_id == patient_id)
        
        total_count = query.count()
        sessions = query.offset(skip).limit(limit).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                "id": session.id,
                "patient_id": session.patient_id,
                "doctor_id": session.doctor_id,
                "monitoring_type": session.monitoring_type.value,
                "gestational_age": session.gestational_age,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "notes": session.notes,
                "doctor_notes": session.doctor_notes,
                "shared_with_doctor": session.shared_with_doctor,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "readings": [],
                "result": None
            })
        
        return {
            "sessions": session_list,
            "total_count": total_count,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    def get_monitoring_session(db, session_id: int, user_id: int, user_role: str) -> Optional[Dict[str, Any]]:
        """Get a specific monitoring session"""
        from app.models.medical import FetalMonitoringSession
        
        session = db.query(FetalMonitoringSession).filter(FetalMonitoringSession.id == str(session_id)).first()
        if not session:
            return None
        
        # Check access permissions
        if user_role == "patient":
            from app.models.medical import Patient
            patient = db.query(Patient).filter(Patient.patient_id == user_id).first()
            if not patient or session.patient_id != patient.id:
                return None
        
        return {
            "id": session.id,
            "patient_id": session.patient_id,
            "doctor_id": session.doctor_id,
            "monitoring_type": session.monitoring_type.value,
            "gestational_age": session.gestational_age,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "notes": session.notes,
            "doctor_notes": session.doctor_notes,
            "shared_with_doctor": session.shared_with_doctor,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "readings": [],
            "result": None
        }
    
    @staticmethod
    def share_session_with_doctor(db, session_id: int, patient_id: int, doctor_id: int) -> Dict[str, Any]:
        """Share a monitoring session with a doctor"""
        from app.models.medical import FetalMonitoringSession, User
        
        # Validate session ownership
        session = db.query(FetalMonitoringSession).filter(
            FetalMonitoringSession.id == str(session_id),
            FetalMonitoringSession.patient_id == patient_id
        ).first()
        
        if not session:
            raise ValueError("Session not found or access denied")
        
        # Validate doctor
        doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
        if not doctor:
            raise ValueError("Doctor not found")
        
        # Update session
        session.doctor_id = doctor_id
        session.shared_with_doctor = True
        db.commit()
        
        return {
            "success": True,
            "message": "Session shared with doctor successfully"
        }
    
    @staticmethod
    def create_pregnancy_info(db, request) -> Dict[str, Any]:
        """Create pregnancy information"""
        from app.models.medical import PregnancyInfo
        
        pregnancy_info = PregnancyInfo(
            patient_id=request.patient_id,
            gestational_age=request.gestational_age,
            last_menstrual_period=request.last_menstrual_period,
            expected_due_date=request.expected_due_date,
            is_high_risk=request.is_high_risk,
            complications=request.complications
        )
        
        db.add(pregnancy_info)
        db.commit()
        db.refresh(pregnancy_info)
        
        return {
            "id": pregnancy_info.id,
            "patient_id": pregnancy_info.patient_id,
            "gestational_age": pregnancy_info.gestational_age,
            "last_menstrual_period": pregnancy_info.last_menstrual_period,
            "expected_due_date": pregnancy_info.expected_due_date,
            "is_high_risk": pregnancy_info.is_high_risk,
            "complications": pregnancy_info.complications,
            "created_at": pregnancy_info.created_at,
            "updated_at": pregnancy_info.updated_at
        }
    
    @staticmethod
    def get_pregnancy_info(db, patient_id: int) -> Optional[Dict[str, Any]]:
        """Get pregnancy information"""
        from app.models.medical import PregnancyInfo
        
        pregnancy_info = db.query(PregnancyInfo).filter(PregnancyInfo.patient_id == patient_id).first()
        if not pregnancy_info:
            return None
        
        return {
            "id": pregnancy_info.id,
            "patient_id": pregnancy_info.patient_id,
            "gestational_age": pregnancy_info.gestational_age,
            "last_menstrual_period": pregnancy_info.last_menstrual_period,
            "expected_due_date": pregnancy_info.expected_due_date,
            "is_high_risk": pregnancy_info.is_high_risk,
            "complications": pregnancy_info.complications,
            "created_at": pregnancy_info.created_at,
            "updated_at": pregnancy_info.updated_at
        }
    
    @staticmethod
    def update_pregnancy_info(db, patient_id: int, request) -> Optional[Dict[str, Any]]:
        """Update pregnancy information"""
        from app.models.medical import PregnancyInfo
        
        pregnancy_info = db.query(PregnancyInfo).filter(PregnancyInfo.patient_id == patient_id).first()
        if not pregnancy_info:
            return None
        
        # Update fields
        if request.gestational_age is not None:
            pregnancy_info.gestational_age = request.gestational_age
        if request.last_menstrual_period is not None:
            pregnancy_info.last_menstrual_period = request.last_menstrual_period
        if request.expected_due_date is not None:
            pregnancy_info.expected_due_date = request.expected_due_date
        if request.is_high_risk is not None:
            pregnancy_info.is_high_risk = request.is_high_risk
        if request.complications is not None:
            pregnancy_info.complications = request.complications
        
        db.commit()
        db.refresh(pregnancy_info)
        
        return {
            "id": pregnancy_info.id,
            "patient_id": pregnancy_info.patient_id,
            "gestational_age": pregnancy_info.gestational_age,
            "last_menstrual_period": pregnancy_info.last_menstrual_period,
            "expected_due_date": pregnancy_info.expected_due_date,
            "is_high_risk": pregnancy_info.is_high_risk,
            "complications": pregnancy_info.complications,
            "created_at": pregnancy_info.created_at,
            "updated_at": pregnancy_info.updated_at
        }
    
    @staticmethod
    def delete_pregnancy_info(db, patient_id: int) -> bool:
        """Delete pregnancy information"""
        from app.models.medical import PregnancyInfo
        
        pregnancy_info = db.query(PregnancyInfo).filter(PregnancyInfo.patient_id == patient_id).first()
        if not pregnancy_info:
            return False
        
        db.delete(pregnancy_info)
        db.commit()
        return True
