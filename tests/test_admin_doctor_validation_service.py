import pytest
from unittest.mock import MagicMock
from app.services import admin_doctor_validation_service
from app.models.medical import Doctor, User

def make_doctor(**kwargs):
    doctor = MagicMock(spec=Doctor)
    for k, v in kwargs.items():
        setattr(doctor, k, v)
    return doctor

def make_user(**kwargs):
    user = MagicMock(spec=User)
    for k, v in kwargs.items():
        setattr(user, k, v)
    return user

def test_count_doctor_validation_requests(mock_db):
    mock_db.query.return_value.filter.return_value.count.return_value = 3
    result = admin_doctor_validation_service.AdminDoctorValidationService.count_doctor_validation_requests(mock_db)
    assert result == 3

def test_list_doctor_validation_requests(mock_db):
    doctors = [make_doctor(id=1, doctor_id=10), make_doctor(id=2, doctor_id=20)]
    users = {10: make_user(name='A', email='a@a.com'), 20: make_user(name='B', email='b@b.com')}
    # Improved side_effect to handle Doctor and User
    def query_side_effect(model):
        mock = MagicMock()
        if model is Doctor:
            mock.filter.return_value.all.return_value = doctors
        elif model is User:
            # .filter().first() should return the user for the given doctor_id
            def filter_side_effect(*a, **k):
                # Simulate .filter(User.id == doctor_id)
                class Dummy:
                    right = MagicMock(value=a[0].right.value if hasattr(a[0], 'right') else 10)
                return MagicMock(first=lambda: users.get(getattr(a[0], 'right', 10)))
            mock.filter.side_effect = filter_side_effect
        else:
            mock.filter.return_value = mock
        return mock
    mock_db.query.side_effect = query_side_effect
    result = admin_doctor_validation_service.AdminDoctorValidationService.list_doctor_validation_requests(mock_db)
    assert isinstance(result, list)
    assert result[0]["doctor_id"] == 10 or result[0]["doctor_id"] == 20

def test_validate_doctor_success(mock_db):
    doctor = make_doctor(id=1)
    mock_db.query.return_value.filter.return_value.first.return_value = doctor
    admin_doctor_validation_service.AdminDoctorValidationService.validate_doctor(mock_db, 1)
    assert doctor.is_valid is True
    mock_db.commit.assert_called()

def test_validate_doctor_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError):
        admin_doctor_validation_service.AdminDoctorValidationService.validate_doctor(mock_db, 99)
