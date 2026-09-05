from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Authenticate using email instead of username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get('email')
        if email is None or password is None:
            return None
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.banned:
                if request.path not in [reverse("ban-page"), reverse("logout")]:
                    return redirect("ban-page")     
        response = self.get_response(request)
        return response