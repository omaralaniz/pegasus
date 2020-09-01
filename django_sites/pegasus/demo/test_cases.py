from . import views
from django.conf import settings
from time import time
import pytest
import logging

'''
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
def test_user_creation(rf):
    request = rf.get('/demo/create_account')
    response = views.create_account(request)
    assert response.status_code == 200


# Verify listing page generates responses relatively quickly
@pytest.mark.django_db
def test_listing_response(rf):
    start = time()
    request = rf.post('/demo/listings', {'city': 'San Francisco'})
    response = views.listing(request)
    assert response.status_code == 200
    end = time()
    runtime = end - start
    logging.info("Listing response time: %s" % runtime)
    assert (runtime < 5)
'''
