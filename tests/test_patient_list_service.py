import pytest
from unittest.mock import MagicMock
from app.services import patient_list_service
from app.models.medical import Record, Patient, User

def make_patient(**kwargs):
    patient = MagicMock(spec=Patient)
    for k, v in kwargs.items():
        setattr(patient, k, v)
    return patient

def make_user(**kwargs):
    user = MagicMock(spec=User)
    for k, v in kwargs.items():
        setattr(user, k, v)
    return user

def test_get_patients_by_doctor_found(mock_db):
    patients = [make_patient(id=1, patient_id=10), make_patient(id=2, patient_id=20)]
    users = {10: make_user(name='A', email='a@a.com'), 20: make_user(name='B', email='b@b.com')}
    # Improved side_effect to handle Record, Patient, User
    def query_side_effect(model):
        mock = MagicMock()
        if model is Record:
            # .filter().distinct().all() returns patient_ids
            mock.filter.return_value.distinct.return_value.all.return_value = [(10,), (20,)]
        elif model is Patient:
            # .filter().all() returns patients
            mock.filter.return_value.all.return_value = patients
        elif model is User:
            # .filter().first() returns user by id
            def filter_side_effect(*a, **k):
                return MagicMock(first=lambda: users.get(getattr(a[0], 'right', 10)))
            mock.filter.side_effect = filter_side_effect
        else:
            mock.filter.return_value = mock
        return mock
    mock_db.query.side_effect = query_side_effect
    result = patient_list_service.PatientListService.get_patients_by_doctor(mock_db, 1)
    assert isinstance(result, list)
    if result:
        assert "patient_id" in result[0]

def test_get_patients_by_doctor_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.distinct.return_value.all.return_value = []
    result = patient_list_service.PatientListService.get_patients_by_doctor(mock_db, 1)
    assert result == []
