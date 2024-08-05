import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from trainers.models import Trainer
from reserve_pers_training.models import Reserve, Schedule, Trainer
from workout_zones.models import Hall

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')

@pytest.fixture
def hall(db):
    return Hall.objects.create(name='Test Hall')

@pytest.fixture
def trainer(db, hall):
    return Trainer.objects.create(name='Test Trainer', hall=hall)

@pytest.fixture
def working_schedule(db, trainer):
    return Schedule.objects.create(trainer=trainer, date='2024-07-30', is_working_day=True)

@pytest.fixture
def non_working_schedule(db, trainer):
    return Schedule.objects.create(trainer=trainer, date='2024-07-31', is_working_day=False)

@pytest.mark.django_db
def test_create_reservation_view(client, user, trainer, working_schedule):
    client.login(username='testuser', password='testpassword')

    url = reverse('create_reservation', kwargs={'trainer_id': trainer.id})
    data = {
        'date': '2024-07-30',
        'start_time': '10:00',
        'end_time': '11:00'
    }
    response = client.post(url, data)

    assert response.status_code == 302  
    assert Reserve.objects.filter(user=user, trainer=trainer, date='2024-07-30', start_time='10:00', end_time='11:00').exists()

@pytest.mark.django_db
def test_trainer_not_available_on_date(client, user, trainer, non_working_schedule):
    client.login(username='testuser', password='testpassword')

    url = reverse('create_reservation', kwargs={'trainer_id': trainer.id})
    data = {
        'date': '2024-07-31',
        'start_time': '10:00',
        'end_time': '11:00'
    }
    response = client.post(url, data)

    assert response.status_code == 200  # Перевірка повернення на ту саму сторінку
    assert 'The trainer is not available on this day. Please choose another date.' in response.context['form'].non_field_errors()


@pytest.mark.django_db
def test_success_reservation_view(client, user):
    client.login(username='testuser', password='testpassword')
    url = reverse('success_reservation')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'testuser@example.com' in response.content.decode()

