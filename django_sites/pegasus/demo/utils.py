from django.contrib.auth.hashers import make_password, check_password
from .models import *


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
