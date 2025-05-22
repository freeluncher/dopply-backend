import pytest
from unittest.mock import MagicMock
from app.services import record_service
from app.models.medical import Record, Patient, User
from types import SimpleNamespace
from datetime import datetime

def make_record(**kwargs):
    # Helper to create a mock Record with patient and patient.user
    record = MagicMock(spec=Record)
    for k, v in kwargs.items():
        setattr(record, k, v)
    return record

def make_user(role="doctor", id=1):
    user = MagicMock(spec=User)
    user.role.value = role
    user.id = id
    return user

def test_get_all_records_returns_all_records(mock_db):
    records = [make_record(id=1), make_record(id=2)]
    mock_db.query.return_value.all.return_value = records
    result = record_service.get_all_records(mock_db)
    assert result == records
    mock_db.query.assert_called_with(Record)

def test_get_all_records_for_user_doctor(mock_db):
    user = make_user(role="doctor", id=10)
    records = [make_record(id=1, patient=SimpleNamespace(user=SimpleNamespace(name="A"))), make_record(id=2, patient=SimpleNamespace(user=SimpleNamespace(name="B")))]
    mock_db.query.return_value.filter.return_value.all.return_value = records
    result = record_service.get_all_records_for_user(mock_db, user)
    assert isinstance(result, list)
    assert result[0]["id"] == 1
    assert result[0]["patient_name"] == "A"
    mock_db.query.assert_any_call(Record)

def test_get_all_records_for_user_patient_found(mock_db):
    user = make_user(role="patient", id=20)
    patient = MagicMock(spec=Patient)
    patient.id = 99
    mock_db.query.return_value.filter.return_value.first.return_value = patient
    records = [make_record(id=3, patient=SimpleNamespace(user=SimpleNamespace(name="C")))]
    # For records query
    def query_side_effect(model):
        if model is Patient:
            return mock_db.query.return_value
        elif model is Record:
            return mock_db.query.return_value
        return None
    mock_db.query.side_effect = query_side_effect
    mock_db.query.return_value.filter.return_value.all.return_value = records
    result = record_service.get_all_records_for_user(mock_db, user)
    assert result[0]["id"] == 3
    assert result[0]["patient_name"] == "C"

def test_get_all_records_for_user_patient_not_found(mock_db):
    user = make_user(role="patient", id=21)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = record_service.get_all_records_for_user(mock_db, user)
    assert result == []

def test_get_all_records_for_user_other_role(mock_db):
    user = make_user(role="admin", id=99)
    result = record_service.get_all_records_for_user(mock_db, user)
    assert result == []
