from login.models import User
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password

class UserBackend(BaseBackend):
    """
    Custom authentication backend.
    """

    def authenticate(self, request, username=None, password=None):
        """
        Overrides Django's auth_user entirely.
        """
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Overrides the get_user method to allow users to log in using their email address.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None