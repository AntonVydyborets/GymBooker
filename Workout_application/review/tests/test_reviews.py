import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from trainers.models import Trainer
from review.models import Review
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
def review_form_data():
    return {
        'review_text': 'Great trainer!',
        'rating': 5
    }

@pytest.fixture
def reviews(db, trainer, user):
    Review.objects.create(review_text='Great trainer', rating=5, trainer=trainer, user=user)
    Review.objects.create(review_text='Not bad trainer', rating=4, trainer=trainer, user=user)

@pytest.mark.django_db
def test_leave_review(client, user, trainer, review_form_data):
    client.login(username='testuser', password='testpassword')

    url = reverse('leave_review', kwargs={'trainer_id': trainer.id})
    response = client.post(url, data=review_form_data)

    assert Review.objects.count() == 1
    review = Review.objects.first()
    assert review.user == user
    assert review.trainer == trainer
    assert review.review_text == 'Great trainer!'
    assert review.rating == 5
    assert response.status_code == 302  
    assert response.url == reverse('trainer_detail', kwargs={'pk': trainer.id})

@pytest.mark.django_db
def test_all_reviews(client, user, trainer, reviews):
    client.login(username='testuser', password='testpassword')
    url = reverse('all_reviews', kwargs={'trainer_id': trainer.id})
    response = client.get(url)

    assert response.status_code == 200
    assert 'reviews' in response.context
    assert len(response.context['reviews']) == 2
    assert response.context['reviews'][0].review_text == 'Great trainer'
    assert response.context['reviews'][1].review_text == 'Not bad trainer'