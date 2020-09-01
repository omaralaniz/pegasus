from . import views
from django.conf import settings
from time import time
import pytest
import logging
from . import utils
from . import models


# Override default pytest behavior and use production database
@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pegasus',
        'USER': 'admin',
        'PASSWORD': 'justD0it!',
        'HOST': '18.224.150.8',
        'PORT': '5432',
    }


# Used to verify pytest is working
# See https://pytest-django.readthedocs.io/en/latest/helpers.html for more examples
def test_tautology():
    assert 1 + 1 == 2


# Verify user creation page is up
def test_user_creation_page(rf):
    request = rf.get('/demo/create_account')
    response = views.create_account(request)
    assert response.status_code == 200


# Verifies user can be properly authenticated with hashed password stored in database
@pytest.mark.django_db
def test_user_authentication():
    username = 'rena2'
    password = 'Twin,16tails'
    auth = utils.AuthBackend()
    user = auth.authenticate(username=username, password=password)
    assert user is not None


@pytest.mark.django_db
def test_user_promotion():
    username = 'shakuntala'
    user = models.RegisteredUser.objects.get(username=username)

    user.promote_student()
    assert user.permission_level == 3

    user.promote_landlord()
    assert user.permission_level == 1

    user.promote_star_tenant()
    assert user.permission_level == 2

    user.promote_admin()
    assert user.is_superuser == True
    assert user.is_staff == True
    assert user.permission_level == 0


# Verify listing page generates responses relatively quickly
@pytest.mark.django_db
def test_listing_response(rf):
    start = time()
    request = rf.post('/demo/listings', {'city': 'San Francisco'})
    request.META['HTTP_HOST'] = 'localhost:8000/'
    response = views.listing(request)
    assert response.status_code == 200
    end = time()
    runtime = end - start
    logging.info("Listing response time: %s" % runtime)
    assert (runtime < 5)
