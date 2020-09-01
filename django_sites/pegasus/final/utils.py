from django.contrib.auth.hashers import make_password, check_password
from .models import *
import requests

SIZE_RANGE = 500


def encrypt_password(password):
    return make_password(password)


def remove_empty_dict(**input_dict):
    filtered_dict = {
        key: value for key, value in input_dict.items() if value is not '' and value is not False and value is not None
    }

    return filtered_dict


class AuthBackend:
    def authenticate(self, username=None, password=None, **kwargs):
        print("[INFO] Received auth request for '%s'." % username)
        try:
            user = RegisteredUser.objects.get(username=username)
            if user:
                user_password = user.password
                if check_password(password, user_password):
                    print("[INFO] Auth success.")
                    return user
                else:
                    print("[ERROR] Password mismatched. Auth rejected.")
                    return None

        except:
            print("[ERROR] Username not found. Auth rejected.")
            return None

    def get_user(self, user_id):
        try:
            return RegisteredUser.objects.get(pk=user_id)
        except:
            return None


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
        city = residence.city
        state = residence.state

        if addr:
            GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' \
                                  + addr + '+' + city + '+' + state \
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


# Returns a set of domiciles based on input filters
def filter_domiciles(**input_filters):

    results = Domicile.objects.all()
    if input_filters:

        # Only pull valid listings
        results = results.filter(is_active=True)

        # If user is provided, also include inactive listings that were posted by that user
        if 'user' in input_filters:
            additional_listings = Domicile.objects.all().filter(owner=input_filters.pop('user'), is_active=False)
            results = results | additional_listings

        # Case-insensitive city search
        if 'city' in input_filters:
            city_value = input_filters.pop('city')
            results = results.filter(city__iexact=city_value)

        # Square footage search +/- SIZE_RANGE
        if 'size' in input_filters:
            size_value = input_filters.pop('size')
            results = results.filter(size__range=(max(0, size_value - SIZE_RANGE), size_value + SIZE_RANGE))

        # Search by min & max prices
        if 'min_price' in input_filters and 'max_price' in input_filters:
            min_value = input_filters.pop('min_price')
            max_value = input_filters.pop('max_price')
            results = results.filter(price__range=(min_value, max_value))
        elif 'min_price' in input_filters:
            min_value = input_filters.pop('min_price')
            results = results.filter(price__gte=min_value)
        elif 'max_price' in input_filters:
            max_value = input_filters.pop('max_price')
            results = results.filter(price__lte=max_value)

        # Case insensitive neighborhood filter
        if 'neighborhood' in input_filters:
            neighborhood_value = input_filters.pop('neighborhood')
            results = results.filter(district__iexact=neighborhood_value)

        results = results.filter(**input_filters)

    return results
