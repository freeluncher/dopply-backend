import pytest
from unittest.mock import MagicMock, patch
from app.services import patient_service
from app.models.medical import Patient, User, Doctor
from app.schemas.patient import PatientUpdate

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

def test_get_patients_returns_all(mock_db):
    patients = [make_patient(patient_id=1), make_patient(patient_id=2)]
    mock_db.query.return_value.all.return_value = patients
    result = patient_service.get_patients(mock_db)
    assert result == patients
    mock_db.query.assert_called_with(Patient)

def test_get_patient_found(mock_db):
    patient = make_patient(patient_id=10)
    mock_db.query.return_value.filter.return_value.first.return_value = patient
    result = patient_service.get_patient(mock_db, 10)
    assert result == patient

def test_get_patient_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = patient_service.get_patient(mock_db, 99)
    assert result is None

@patch('app.services.patient_service.get_password_hash', return_value='hashed')
def test_update_patient_success(mock_hash, mock_db):
    import datetime
    patient = make_patient(patient_id=5)
    user = make_user(id=5)
    mock_db.query.return_value.filter.return_value.first.side_effect = [patient, user]
    data = PatientUpdate(name='A', email='a@b.com', password='pw', birth_date=datetime.date(2024, 1, 1), address='Addr', medical_note='Note')
    result = patient_service.update_patient(mock_db, 5, data)
    assert result == patient
    assert user.name == 'A'
    assert user.email == 'a@b.com'
    assert user.password_hash == 'hashed'
    assert patient.birth_date == datetime.date(2024, 1, 1)
    assert patient.address == 'Addr'
    assert patient.medical_note == 'Note'
    mock_db.commit.assert_called()
    mock_db.refresh.assert_called_with(patient)

def test_update_patient_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    data = PatientUpdate()
    result = patient_service.update_patient(mock_db, 123, data)
    assert result is None

def test_delete_patient_success(mock_db):
    patient = make_patient(patient_id=7)
    user = make_user(id=7)
    mock_db.query.return_value.filter.return_value.first.side_effect = [patient, user]
    result = patient_service.delete_patient(mock_db, 7)
    assert result is True
    mock_db.delete.assert_any_call(patient)
    mock_db.delete.assert_any_call(user)
    mock_db.commit.assert_called()

def test_delete_patient_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    result = patient_service.delete_patient(mock_db, 77)
    assert result is False
    mock_db.commit.assert_not_called()

@patch('app.services.patient_service.get_password_hash', return_value='hashed')
def test_register_user_universal_new_patient(mock_hash, mock_db):
    # Simulate no user found
    mock_db.query.return_value.filter.return_value.first.return_value = None
    data = MagicMock()
    data.email = 'a@b.com'
    data.password = 'pw'
    data.name = 'A'
    data.role = 'patient'
    data.birth_date = '2024-01-01'
    data.address = 'Addr'
    data.medical_note = 'Note'
    user = make_user(id=1, name='A', email='a@b.com', password_hash='hashed', role='patient')
    patient = make_patient(patient_id=1, birth_date='2024-01-01', address='Addr', medical_note='Note')
    # Simulate add/commit/refresh
    def add_side_effect(obj):
        if isinstance(obj, User):
            mock_db.refresh(obj)
        if isinstance(obj, Patient):
            mock_db.refresh(obj)
    mock_db.add.side_effect = add_side_effect
    mock_db.refresh.side_effect = lambda obj: None
    with patch('app.services.patient_service.User', return_value=user), \
         patch('app.services.patient_service.Patient', return_value=patient):
        result = patient_service.register_user_universal(mock_db, data)
        assert result == user
        mock_db.add.assert_any_call(user)
        mock_db.add.assert_any_call(patient)
        mock_db.commit.assert_called()

# Anda bisa menambah test untuk doctor dan aktivasi pasien jika diinginkan
