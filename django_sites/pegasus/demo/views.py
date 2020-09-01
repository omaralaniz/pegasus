from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from . import utils
from .forms import *
from .models import *
from pprint import pprint
import requests
import logging






# TODO: View stubs
def add_new_property(request):
    return render(request, 'demo/add_new_property.html')


def description(request):
    return render(request, 'demo/description.html')


def manager_profile(request):
    return render(request, 'demo/manager_profile.html')


def survey(request):
    return render(request, 'demo/survey.html')


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            # Filter all null values from filter set
            filters = {
                key: value for key, value in form.cleaned_data.items()
                if value is not '' and value is not False and value is not None and '%s'.lower() % value != 'all'
            }

            # Separate domicile filters
            domicile_filters = {
                key: value for key, value in filters.items() if key in Domicile.__dict__
            }
            all(map(filters.pop, domicile_filters))
            logging.debug("Listing filters: %s" % filters)

            for key, value in domicile_filters.items():
                logging.debug("Domicile filter: (%s, %s)" % (key, value))

            results = Domicile.objects.all()
            # Filter domiciles
            if domicile_filters:
                # Case-insensitive city search
                if 'city' in domicile_filters:
                    city_value = domicile_filters.pop('city')
                    results = results.filter(city__iexact=city_value).filter(**domicile_filters)
                else:
                    results = results.filter(**domicile_filters)

            listings = ValidListing.objects.all().filter(pk__in=results).filter(**filters)

            # Filter domiciles from filtered listings
            if filters:
                results = results.filter(pk__in=listings)

            searched_lat_lng = get_lat_long(results)

            for key, value in filters.items():
                logging.debug("Search filters: (%s , %s)" % (key, value))

            for entry in listings:
                try:
                    logging.debug(entry.photo.url)
                except ValueError as exception:
                    logging.warning(exception)

            context = {
                'form': form,
                'search_results': results,
                'listing_results': listings,
                'search_count': len(results),
                'lat_lng': searched_lat_lng
            }
            return render(request, 'demo/listing.html', {'context': context})

    else:
        form = SearchForm()
    context = {
        'form': form,
        'search_results': []
    }
    return render(request, 'demo/index.html', {'context': context})


# LISTING PAGES #
def listing(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            # Filter all null values from filter set
            filters = {
                key: value for key, value in form.cleaned_data.items()
                if value is not '' and value is not False and value is not None and '%s'.lower() % value != 'all'
            }

            # Separate domicile filters
            domicile_filters = {
                key: value for key, value in filters.items() if key in Domicile.__dict__
            }
            all(map(filters.pop, domicile_filters))
            logging.debug("Listing filters: %s" % filters)

            for key, value in domicile_filters.items():
                logging.debug("Domicile filter: (%s, %s)" % (key, value))

            results = Domicile.objects.all()
            # Filter domiciles
            if domicile_filters:
                # Case-insensitive city search
                if 'city' in domicile_filters:
                    city_value = domicile_filters.pop('city')
                    results = results.filter(city__iexact=city_value)

                # Filter for square footage
                if 'size' in domicile_filters:
                    size = domicile_filters.pop('size')
                    results = results.filter(size__gte=size)

                results = results.filter(**domicile_filters)

            listings = ValidListing.objects.all().filter(pk__in=results).filter(**filters)

            # Filter domiciles from filtered listings
            if filters:
                results = results.filter(pk__in=listings)

            searched_lat_lng = get_lat_long(results)

            for key, value in filters.items():
                logging.debug("Search filters: (%s , %s)" % (key, value))

            for entry in listings:
                try:
                    logging.debug(entry.photo.url)
                except ValueError as exception:
                    logging.warning(exception)

            context = {
                'form': form,
                'search_results': results,
                'listing_results': listings,
                'search_count': len(results),
                'lat_lng': searched_lat_lng
            }
            return render(request, 'demo/listing.html', {'context': context})

    else:
        form = SearchForm()

    # Should have some default listings displayed (maybe most recent?)
    context = {
        'form': form,
        'search_results': []
    }
    return render(request, 'demo/listing.html', {'context': context})


@login_required
def create_listing(request):
    if request.method == 'POST':
        domicile_form = CreateDomicileForm(request.POST)
        listing_form = CreateListingForm(request.POST)

        if domicile_form.is_valid() and listing_form.is_valid():
            for key, value in domicile_form.cleaned_data.items():
                logging.debug("(%s, %s)" % (key, value))
            for key, value in listing_form.cleaned_data.items():
                logging.debug("(%s, %s)" % (key, value))

            try:
                logging.info("Creating new residence...")

                owner = listing_form.cleaned_data.pop('owner')
                owner_exists = len(VerifiedUser.objects.all().filter(username=owner)) >= 1
                if not owner_exists:
                    raise KeyError("Owner '%s' not found." % owner)

                domicile = Domicile()
                domicile.update(**domicile_form.cleaned_data)
                domicile.save()

                logging.info("Creating new listing...")
                listing = ValidListing()
                listing.update(**listing_form.cleaned_data)
                listing.residence = domicile
                listing.save()

            except Exception as error_message:
                logging.error("Operation failed: %s" % error_message)
    else:
        domicile_form = CreateDomicileForm()
        listing_form = CreateListingForm()

    context = {
        'domicile_form': domicile_form,
        'listing_form': listing_form
    }

    return render(request, 'demo/add_new_property.html', {'context': context})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(ValidListing, pk=listing_id)

    if request.method == 'POST':
        form = EditListingForm(request.POST)

        if form.is_valid():
            try:
                logging.info("Editing listing '%s'..." % listing_id)
                listing.update(**form.cleaned_data)
                listing.save()

                context = {
                    'form': form,
                    'update_success': True,
                    'error_message': ''
                }
            except Exception as error_message:
                context = {
                    'form': form,
                    'update_success': False,
                    'error_message': '%s' % error_message
                }
        else:
            context = {
                'form': form,
                'update_success': False,
                'error_message': '%s' % form.errors
            }
    else:
        form = EditListingForm(instance=listing)
        context = {
            'form': form,
            'update_success': False,
            'error_message': ''
        }

    if context['error_message']:
        logging.error("Edit operation failed: %s" % context['error_message'])
    return render(request, "demo/modify_listing.html", {'context': context})


@login_required
def view_listing(request, listing_id):
    listing = get_object_or_404(ValidListing, pk=listing_id)
    domicile = listing.residence
    full_address = domicile.address + " " + domicile.city + " " + domicile.state + " " + str(domicile.zip_code)

    # get_lat_long takes a list of listings as argument and returns a list of dicts
    lat_long = get_lat_long([domicile])

    # Get the single dictionary
    single_lat_long = lat_long[0]

    context = {
        'listing': listing,
        'domicile': domicile,
        'address': full_address,
        'lat_long': single_lat_long,
    }
    return render(request, 'demo/description.html', {'context': context})


# USER PAGES #
def create_account(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_attributes = {
                key: value for key, value in form.cleaned_data.items()
            }

            # Encrypt password before creating account
            user_attributes.pop('confirm_password')
            secret = '%s' % user_attributes.get('password', '')
            secret = utils.encrypt_password(secret)
            user_attributes['password'] = secret

            try:
                logging.info("Creating new user...")
                user = RegisteredUser()
                user.update(**user_attributes)
                user.save()
                logging.info("Created user '%s'." % user.email)

                # User creation success, now send email to activate full account
                current_site = get_current_site(request)
                mail_subject = 'Pegasus account registration'
                message = render_to_string('registration/signup_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.username)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
                logging.info("Sent confirmation email to user '%s' for activation." % email)
                return render(request, 'demo/login_confirmation.html')

            except Exception as error_message:
                context = {
                    'form': form,
                    'creation_success': False,
                    'form_submitted': True,
                    'error_message': '%s' % error_message
                }

        else:
            context = {
                'form': form,
                'creation_success': False,
                'form_submitted': False,
                'error_message': '%s' % form.errors
            }

    else:
        form = CreateUserForm()
        context = {
            'form': form,
            'creation_success': False,
            'form_submitted': False,
            'error_message': ''
        }

    return render(request, 'demo/create_account.html', {'context': context})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = RegisteredUser.objects.get(username=uid)
    except (TypeError, ValueError, RegisteredUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        # Coerce registered user to verified user first. Then promote to either Student or Landlord
        user.is_active = True
        user.__class__ = VerifiedUser
        user.save(force_insert=True)

        if user.is_student:
            user.__class__ = Student
        else:
            user.__class__ = Landlord
        user.save(force_insert=True)

        login(request, user, backend='demo.utils.AuthBackend')
        return HttpResponse('Thank you for your email confirmation. You may now login with your account.')
    else:
        if user is not None:
            logging.warning("Got invalid token activation from user '%s'." % user.username)
        return HttpResponse('Activation link is invalid!')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form_data = {
                key: value for key, value in form.cleaned_data.items()
            }

            username = form_data['username']
            password = form_data['password']
            auth_backend = utils.AuthBackend()
            user = auth_backend.authenticate(
                username=username, password=password)

            logging.info("Got login request from '%s'." % username)

            # Login success
            if user is not None:
                logging.info("Login success.")
                login(request, user, backend='demo.utils.AuthBackend')

                # Check if user needs to redirect to another page other than index
                next_url = request.POST.get('next', '')
                if next_url:
                    return redirect(next_url)
                else:
                    return HttpResponseRedirect(reverse('index'))

            # Login failure
            else:
                logging.info("Login failure. Check username or password.")
                context = {
                    'login_form': form,
                    'error_message': 'Username or password is incorrect.'
                }

        else:
            context = {
                'login_form': form,
                'error_message': '%s' % form.errors
            }

    else:
        form = LoginForm()
        context = {
            'login_form': form,
            'error_message': ''
        }
    return render(request, 'demo/login.html', {'context': context})


@login_required
def compatibility_score(request):
    if request.method == 'POST':
        compatibility_form = CompatibilityScoreForm(request.POST)
        if compatibility_form.is_valid():
            pass

    else:
        compatibility_form = CompatibilityScoreForm()

    context = {
        'form': compatibility_form
    }

    return render(request, 'demo/compatibility_score.html', {'context': context})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def view_profile(request, username=None):
    try:

        # If no username is provided, default to currently logged in account
        if username is None:
            username = request.user.username

        user_instance = RegisteredUser.objects.get(username=username)
        if user_instance:
            context = {
                'user_found': True,
                'user': user_instance,
                'error_message': ''
            }
        else:
            context = {
                'user_found': False,
                'user': None,
                'error_message': "User '%s' not found." % username
            }

    except Exception as error_message:
        context = {
            'user_found': False,
            'user': None,
            'error_message': "User '%s' not found." % username
        }

    return render(request, 'demo/view_profile.html', {'context': context})


@login_required
def modify_profile(request):
    current_user = request.user.username
    user_instance = RegisteredUser.objects.get(username=current_user)

    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            user_attributes = {
                key: value for key, value in form.cleaned_data.items()
            }

            try:
                user_instance.update(**user_attributes)
                user_instance.save()

                context = {
                    'form': form,
                    'update_success': True,
                    'error_message': ''
                }

            except Exception as error_message:
                context = {
                    'form': form,
                    'update_success': False,
                    'error_message': '%s' % error_message
                }

        else:
            context = {
                'form': form,
                'update_success': False,
                'error_message': '%s.' % form.errors
            }

    else:
        form = EditUserForm(instance=user_instance)
        context = {
            'form': form,
            'update_success': False,
            'error_message': ''
        }
    return render(request, 'demo/modify_profile.html', {'context': context})


@login_required
def delete_user(request):
    if request.method == 'POST':
        form = DeleteUserForm(request.POST)
        if form.is_valid():
            pass

    else:
        form = DeleteUserForm()

    context = {
        'form': form
    }

    return render(request, 'demo/delete_account.html', {'context': context})


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            pass

    else:
        form = ForgotPasswordForm()

    context = {
        'form': form
    }

    return render(request, 'demo/forgot_password.html', {'context': context})


# Get geocoding data (lat / long) for searched listings
def get_lat_long(residences):
    # List of dictionaries {'lat': xxx, 'lng':xxx}
    all_lat_lng = []
    for residence in residences:
        geodata = {
            'lat': 0,
            'lng': 0
        }
        addr = residence.address

        if addr:
            GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' \
                                  + addr \
                                  + '&key=AIzaSyCbr6KeU9un_uLPpH581LUfOb8PE3zi1x0'
            params = {'address': addr}
            map_request = requests.get(GOOGLE_MAPS_API_URL, params=params)
            response = map_request.json()

            if len(response['results']) > 0:
                result = response['results'][0]
                geodata['lat'] = result['geometry']['location']['lat']
                geodata['lng'] = result['geometry']['location']['lng']
                all_lat_lng.append(geodata)
    return all_lat_lng


#TODO: remove once functional
def maps(request):
    listings = ValidListing.objects.all()
    for listing in listings:
        print(listing.residence.address)

    # Holds geocoding data for all addresses (each of which is a dictionary)
    all_lat_lng = []
    for listing in listings:

        geodata = dict()
        geodata['lat'] = 0
        geodata['lng'] = 0
        addr = listing.residence.address

        if addr:
            GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + addr + '&key=AIzaSyCbr6KeU9un_uLPpH581LUfOb8PE3zi1x0'

            params = {'address': addr}

            map_request = requests.get(GOOGLE_MAPS_API_URL, params=params)
            response = map_request.json()
            # print('response: ', response)

            if len(response['results']) > 0:
                result = response['results'][0]
                geodata['lat'] = result['geometry']['location']['lat']
                geodata['lng'] = result['geometry']['location']['lng']
                all_lat_lng.append(geodata)

    context = {
        'addresses': listings,
        'latitude': geodata['lat'],
        'longitude': geodata['lng'],
        'all_lat_lng': all_lat_lng,
    }
    pprint(context)
    return render(request, 'demo/maps.html', context)


    