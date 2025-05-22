import pytest
from unittest.mock import MagicMock
from app.services import monitoring_service
from app.models.medical import Record, Patient
from datetime import datetime

def make_patient(**kwargs):
    patient = MagicMock(spec=Patient)
    for k, v in kwargs.items():
        setattr(patient, k, v)
    return patient

def test_process_monitoring_result_success(mock_db):
    patient = make_patient(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = patient
    mock_db.add.side_effect = lambda obj: None
    mock_db.commit.side_effect = lambda: None
    mock_db.refresh.side_effect = lambda obj: None
    result = monitoring_service.MonitoringService.process_monitoring_result(mock_db, 1, [70, 75, 80], "note")
    assert result["classification"] == "normal"
    assert result["patient_id"] == 1
    assert result["doctor_note"] == "note"

def test_process_monitoring_result_patient_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError):
        monitoring_service.MonitoringService.process_monitoring_result(mock_db, 1, [70, 75, 80])

def test_classify_bpm_normal():
    data = [{"time": 1, "bpm": 70}, {"time": 2, "bpm": 75}]
    result = monitoring_service.MonitoringService.classify_bpm(data)
    assert result["result"] == "normal"
    assert result["classification"] == "normal"

def test_classify_bpm_brady():
    data = [{"time": 1, "bpm": 50}, {"time": 2, "bpm": 55}]
    result = monitoring_service.MonitoringService.classify_bpm(data)
    assert result["classification"] == "bradikardia"

def test_save_monitoring_record_patient_not_found(mock_db):
    req = MagicMock()
    req.patient_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError):
        monitoring_service.MonitoringService.save_monitoring_record(mock_db, req)
