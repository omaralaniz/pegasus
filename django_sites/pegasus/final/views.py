from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .forms import *
from .models import *
from . import utils
from pprint import pprint
import logging
import json


# For use to determine which URL to hit, based on where server sits
def get_media_base_url(request):
    domain = request.META['HTTP_HOST']
    if 'localhost' in domain or '127.0.01' in domain:
        media_base = domain
    else:
        media_base = domain + '/web'
    return media_base


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            # Filter all null values from filter set
            filters = {
                key: value for key, value in form.cleaned_data.items()
                if value is not '' and value is not False and value is not None and '%s'.lower() % value != 'all'
            }

            # Only search for active listings, or listings that belong to the current user (if there is one)
            try:
                filters['user'] = request.user.username
            except:
                pass

            results = utils.filter_domiciles(**filters)
            searched_lat_lng = utils.get_lat_long(results)

            for key, value in filters.items():
                logging.debug("Search filters: (%s , %s)" % (key, value))

            for entry in results:
                try:
                    logging.debug(entry.photo.url)
                except ValueError as exception:
                    logging.warning(exception)

            context = {
                'form': form,
                'search_results': results,
                'search_count': len(results),
                'lat_lng': searched_lat_lng,
                'media_base': get_media_base_url(request)
            }
            return render(request, 'final/listing.html', {'context': context})

    else:
        form = SearchForm()

    context = {
        'form': form,
        'search_results': [],
        'media_base': get_media_base_url(request)
    }
    return render(request, 'final/index.html', {'context': context})


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

            results = utils.filter_domiciles(**filters)
            searched_lat_lng = utils.get_lat_long(results)

            for key, value in filters.items():
                logging.debug("Search filters: (%s , %s)" % (key, value))

            for entry in results:
                try:
                    logging.debug(entry.photo.url)
                except ValueError as exception:
                    logging.warning(exception)

            context = {
                'form': form,
                'search_results': results,
                'search_count': len(results),
                'lat_lng': searched_lat_lng,
                'media_base': get_media_base_url(request)
            }

            return render(request, 'final/listing.html', {'context': context})

    else:
        form = SearchForm()

    context = {
        'form': form,
        'search_results': [],
        'media_base': get_media_base_url(request)
    }

    return render(request, 'final/listing.html', {'context': context})


@login_required
def create_listing(request):
    error_message = ''
    if request.method == 'POST':
        form = CreateDomicileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                logging.info("Creating new residence...\n%s" % json.dumps('%s' % form.cleaned_data, indent=4))
                owner = request.user.username
                owner_exists = len(RegisteredUser.objects.all().filter(username=owner)) >= 1
                if not owner_exists:
                    raise KeyError("Owner '%s' not found." % owner)

                form.cleaned_data['owner'] = owner

                domicile = Domicile()
                domicile.update(**form.cleaned_data)
                domicile.is_active = False
                domicile.save()

                # Domicile has been created, now submit email
                mail_subject = 'Pegasus listing submission'
                message = render_to_string('final/property_confirmation_email.html', {
                    'user': request.user,
                    'domain': request.META['HTTP_HOST'],
                    'listing': domicile
                })
                email = EmailMessage(mail_subject, message, to=[request.user.email])
                email.send()
                logging.info("Sent confirmation email to user '%s' for listing." % email)
                return render(request, 'final/property_confirmation.html')

            except Exception as exception_message:
                logging.error("Operation failed: %s" % exception_message)
                error_message = exception_message

    else:
        form = CreateDomicileForm()

    context = {
        'form': form,
        'error_message': error_message
    }

    pprint(context)
    return render(request, 'final/add_new_property.html', {'context': context})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Domicile, pk=listing_id)

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

    context["domain"] = request.META['HTTP_HOST']
    return render(request, "final/modify_listing.html", {'context': context})


@login_required
def edit_listing_photo(request, listing_id):
    listing = get_object_or_404(Domicile, pk=listing_id)

    # Verify current user is owner. Otherwise, raise 404 error
    current_user = request.user.username
    if listing.owner != current_user:
        raise Http404()

    # Get initial photo data for listing
    photos = DomicilePhoto.objects.filter(listing=listing)
    initial_photo_data = [{'photo_url': x.photo_url, 'action': 'N'} for x in photos]
    update_success = False
    error_message = ''

    if request.method == 'POST':
        formset = EditPhotoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            try:
                logging.info("Editing listing '%s'..." % listing_id)

                # Build log of operations
                actions = '\n'
                for counter, form in enumerate(formset):
                    actions = actions + 'Action %s: %s, URL: %s\n' % (
                        counter, form.cleaned_data.get('action', ''), form.cleaned_data.get('photo_url', '')
                    )
                logging.info("Actions to be taken: %s" % actions)
                deletion_occurred = False

                for counter, form in enumerate(formset):
                    action_type = form.cleaned_data.get('action', '')
                    photo_url = form.cleaned_data.get('photo_url', '')

                    # Add Image
                    if action_type == 'A':
                        if photo_url:
                            logging.info("Adding new image...")
                            image = DomicilePhoto()
                            image.photo_url = photo_url
                            image.listing = listing
                            image.save()

                    # Delete Image
                    if action_type == 'D':
                        logging.info("Deleting image...")
                        image = photos[counter]
                        image.delete()
                        deletion_occurred = True

                update_success = True

                # On photo delete, also clear out any null-valued images from DB
                if deletion_occurred:
                    photos = DomicilePhoto.objects.filter(listing=listing, photo_url='')
                    [photo.delete() for photo in photos]

                # On update success, update formset to include edited photos and reload page
                photos = DomicilePhoto.objects.filter(listing=listing)
                initial_photo_data = [{'photo_url': x.photo_url, 'action': 'N'} for x in photos]
                formset = EditPhotoFormSet(initial=initial_photo_data)

            except Exception as exception:
                error_message = exception

        else:
            logging.info("Failed formset edit: %s" % formset.errors)
            error_message = formset.errors
            formset = EditPhotoFormSet(initial=initial_photo_data)
    else:
        formset = EditPhotoFormSet(initial=initial_photo_data)

    context = {
        'formset': formset,
        'update_success': update_success,
        'error_message': error_message
    }
    if error_message:
        logging.error("Edit operation failed: %s" % context['error_message'])

    return render(request, "final/modify_listing_photo.html", {'context': context})


@login_required
def view_listing(request, listing_id):
    domicile = get_object_or_404(Domicile, pk=listing_id)
    full_address = domicile.address + " " + domicile.city + " " + domicile.state + " " + str(domicile.zip_code)

    photos = DomicilePhoto.objects.filter(listing=domicile)
    photo_urls = [x.photo_url.url for x in photos]

    # get_lat_long takes a list of listings as argument and returns a list of dicts
    lat_long = utils.get_lat_long([domicile])

    # Get the single dictionary
    single_lat_long = lat_long[0]

    context = {
        'listing': listing,
        'domicile': domicile,
        'address': full_address,
        'lat_long': single_lat_long,
        'listing_photos': photo_urls,
        'viewer_is_owner': request.user.username == domicile.owner
    }
    pprint(context)
    return render(request, 'final/description.html', {'context': context})


# USER PAGES #
def create_account(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user_attributes = {
                key: value for key, value in form.cleaned_data.items()
            }

            try:
                logging.info("Creating new user...")
                user = RegisteredUser()

                # Check passwords match
                secret = '%s' % user_attributes.get('password', '')
                confirm_secret = '%s' % user_attributes.get('confirm_password', '')
                if secret != confirm_secret:
                    raise ValueError("Passwords do not match!")

                # Check email is SFSU, but only for student accounts
                account_status = user_attributes.get('student_account', '')
                if account_status == 'Y':
                    email_address = user_attributes.get('email', '')
                    email_address = email_address.strip().lower()
                    if not email_address.endswith('@mail.sfsu.edu'):
                        raise ValueError("Only SFSU EDU accounts are allowed.")

                # Encrypt password before creating account
                user_attributes.pop('confirm_password')
                secret = utils.encrypt_password(secret)
                user_attributes['password'] = secret

                student_account = user_attributes.pop('student_account')
                user.is_student = student_account == 'Y'

                user.update(**user_attributes)
                user.save()
                logging.info("Created user '%s'." % user.email)

                # User creation success, now send email to activate full account
                mail_subject = 'Pegasus account registration'
                message = render_to_string('registration/signup_email.html', {
                    'user': user,
                    'domain': request.META['HTTP_HOST'],
                    'uid': urlsafe_base64_encode(force_bytes(user.username)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.send()
                logging.info("Sent confirmation email to user '%s' for activation." % email)
                return render(request, 'final/login_confirmation.html')

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

    pprint(context)

    return render(request, 'final/create_account.html', {'context': context})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = RegisteredUser.objects.get(username=uid)
    except (TypeError, ValueError, RegisteredUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        # Activate user account
        user.activate_account()

        if user.is_student:
            user.promote_student()
        else:
            user.promote_landlord()

        login(request, user, backend='final.utils.AuthBackend')
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
                login(request, user, backend='final.utils.AuthBackend')

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
    return render(request, 'final/login.html', {'context': context})


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

    return render(request, 'final/compatibility_score.html', {'context': context})


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
    context['media_base'] = get_media_base_url(request)
    return render(request, 'final/view_profile.html', {'context': context})


@login_required
def modify_profile(request):
    current_user = request.user.username
    user_instance = RegisteredUser.objects.get(username=current_user)

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=user_instance)
        if form.is_valid():
            user_attributes = {
                key: value for key, value in form.cleaned_data.items()
            }

            pprint(user_attributes)

            try:
                user_instance.update(**user_attributes)
                user_instance.save()

                context = {
                    'update_success': True,
                    'error_message': ''
                }

            except Exception as error_message:
                context = {
                    'update_success': False,
                    'error_message': '%s' % error_message
                }

        else:
            context = {
                'update_success': False,
                'error_message': '%s.' % form.errors
            }

    else:
        context = {
            'update_success': False,
            'error_message': ''
        }

    # If update is succesful, refresh instance
    if context['update_success']:
        user_instance = RegisteredUser.objects.get(username=current_user)
    context['form'] = EditUserForm(instance=user_instance)

    pprint(context)
    return render(request, 'final/modify_profile.html', {'context': context})


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

    return render(request, 'final/delete_account.html', {'context': context})


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

    return render(request, 'final/forgot_password.html', {'context': context})
