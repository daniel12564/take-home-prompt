import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.mark.django_db
@pytest.mark.parametrize('model', ['accounts/account', 'activity/activityevent'])
def test_models_are_listed_in_the_admin(model):
    admin_user = get_user_model().objects.create_superuser('admin', 'a@example.com', 'pw')
    client = Client()
    client.force_login(admin_user)

    response = client.get(f'/admin/{model}/')

    assert response.status_code == 200
