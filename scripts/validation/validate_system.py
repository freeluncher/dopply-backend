"""
Validation script for fetal monitoring system
Tests imports and basic functionality
"""

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        from app.models.medical import (
            FetalMonitoringSession, FetalHeartRateReading, 
            FetalMonitoringResult, PregnancyInfo
        )
        print("✅ Models import successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from app.schemas.fetal_monitoring import (
            FetalClassificationRequest, FetalClassificationResponse,
            FetalMonitoringSessionCreate, FetalMonitoringSessionResponse
        )
        print("✅ Schemas import successfully")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        from app.services.fetal_monitoring_service import FetalMonitoringService
        print("✅ Service imports successfully")
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False
    
    try:
        from app.api.v1.endpoints.fetal_monitoring import router
        print("✅ Endpoint imports successfully")
    except Exception as e:
        print(f"❌ Endpoint import failed: {e}")
        return False
    
    try:
        from app.main import app
        print("✅ Main app imports successfully")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and models"""
    print("🗄️ Testing database connection...")
    
    try:
        from app.db.session import SessionLocal
        from app.models.medical import User, Patient, FetalMonitoringSession
        
        db = SessionLocal()
        
        # Test basic queries
        user_count = db.query(User).count()
        patient_count = db.query(Patient).count()
        session_count = db.query(FetalMonitoringSession).count()
        
        print(f"✅ Database connected: {user_count} users, {patient_count} patients, {session_count} fetal sessions")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_service_functionality():
    """Test service functionality"""
    print("⚙️ Testing service functionality...")
    
    try:
        from app.services.fetal_monitoring_service import FetalMonitoringService
        from datetime import datetime
        
        # Test classification logic
        fhr_data = [
            {"timestamp": datetime.now(), "bpm": 140, "signal_quality": 0.85},
            {"timestamp": datetime.now(), "bpm": 142, "signal_quality": 0.87},
            {"timestamp": datetime.now(), "bpm": 138, "signal_quality": 0.83}
        ]
        
        result = FetalMonitoringService.classify_fetal_heart_rate(
            fhr_data=fhr_data,
            gestational_age=32,
            maternal_age=28,
            duration_minutes=30
        )
        
        print(f"✅ Classification service works: {result['overall_classification']}")
        return True
    except Exception as e:
        print(f"❌ Service functionality failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Fetal Monitoring System Validation")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    print()
    
    # Test database
    if not test_database_connection():
        success = False
    
    print()
    
    # Test service
    if not test_service_functionality():
        success = False
    
    print()
    print("=" * 50)
    
    if success:
        print("🎉 All validations passed! System is ready.")
        print("📝 Next steps:")
        print("   1. Start server: uvicorn app.main:app --reload")
        print("   2. Test endpoints at: http://localhost:8000/docs")
        print("   3. Login with: gandhi1245 (all users)")
    else:
        print("❌ Some validations failed. Please check the errors above.")

if __name__ == "__main__":
    main()
